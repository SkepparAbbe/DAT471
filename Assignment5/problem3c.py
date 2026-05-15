#!/usr/bin/env python3

import argparse
import sys
import os
from pyspark import SparkContext, SparkConf
import math
import string
import time
import numpy as np
from assignment5_problem1_skeleton import murmur3_32
from assignment5_problem2_skeleton import rho

def compute_jr(key,seed,log2m):
    """hash the string key with murmur3_32, using the given seed
    then take the **least significant** log2(m) bits as j
    then compute the rho value **from the left**

    E.g., if m = 1024 and we compute hash value 0x70ffec73
    or 0b01110000111111111110110001110011
    then j = 0b0001110011 = 115
         r = 2
         since the 2nd digit of 0111000011111111111011 is the first 1

    Return a tuple (j,r) of integers
    """
    h = murmur3_32(key,seed)
    j = ~(0xffffffff << log2m) & h
    r = rho(h)
    return j, r

def auto_int(x):
    """Auxiliary function to help convert e.g. hex integers"""
    return int(x,0)

def dlog2(n):
    return n.bit_length() - 1

def get_files(path):
    """
    A generator function: Iterates through all .txt files in the path and
    returns the content of the files

    Parameters:
    - path : string, path to walk through

    Yields:
    The content of the files as strings
    """
    for (root, dirs, files) in os.walk(path):
        for file in files:
            if file.endswith('.txt'):
                path = f'{root}/{file}'
                with open(path,'r') as f:
                    yield f.read()

def alpha(m):
    """Auxiliary function: bias correction"""
    if m == 16:
        return 0.673
    elif m == 32:
        return 0.697
    elif m == 64:
        return 0.709
    else:
        return (0.7213/(1+1.079/m))
        
def hyperloglog(words, m, seed, log2m):
    num_pairs, harmonic_sum = words \
        .map(lambda w: compute_jr(w, seed, log2m)) \
        .reduceByKey(max) \
        .map(lambda jr: (1, 2**(-jr[1]))) \
        .reduce(lambda a, b: (a[0]+b[0], a[1]+b[1]))
    
    num_zeros = m - num_pairs
    n_hat = alpha(m) * m**2 * (1 / (harmonic_sum + num_zeros))

    if (n_hat <= ((5/2) * m)) and (num_zeros > 0):
        n_hat = m * math.log(m/num_zeros)
    elif (n_hat > ((1/30) * 2**32)):
        n_hat = -2**32 * math.log(1-(n_hat / 2**32))

    return n_hat

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Using HyperLogLog, computes the approximate number of '
            'distinct words in all .txt files under the given path.'
    )
    parser.add_argument('path',help='path to walk',type=str)
    parser.add_argument('-m','--num-registers',type=int,required=True,
                            help=('number of registers (must be a power of two)'))
    parser.add_argument('-w','--num-workers',type=int,default=1,
                        help='number of Spark workers')
    args = parser.parse_args()

    m = args.num_registers
    if m <= 0 or (m&(m-1)) != 0:
        sys.stderr.write(f'{sys.argv[0]}: m must be a positive power of 2\n')
        quit(1)
    log2m = dlog2(m)

    num_workers = args.num_workers
    if num_workers < 1:
        sys.stderr.write(f'{sys.argv[0]}: must have a positive number of '
                         'workers\n')
        quit(1)

    path = args.path
    if not os.path.isdir(path):
        sys.stderr.write(f"{sys.argv[0]}: `{path}' is not a valid directory\n")
        quit(1)

    start = time.time()
    conf = SparkConf()
    conf.setMaster(f'local[{num_workers}]')
    conf.set('spark.driver.memory', '128g')
    conf.set("spark.ui.showConsoleProgress", "false")
    sc = SparkContext(conf=conf)

    data = sc.parallelize(get_files(path))
    words = data.flatMap(lambda x: x.split()).cache()

    rng = np.random.default_rng(seed=1337)
    seeds = rng.choice(2**32, 1000, replace=False)
    values = [0] * 1000

    for i, s in enumerate(seeds):
        estimate = hyperloglog(words, m, s, log2m)
        values[i] = estimate

    values = np.array(values)
    np.save('values.npy', values)

    mean = np.mean(values)
    std = np.std(values)

    print(f"The arithmetic mean of the hash values is: {mean}")
    print(f"The standard deviation of the hash values is: {std}")
    print("-"*20)

    n = 284689

    for k in range(1,4):
        low = n*(1-k*(1.04/math.sqrt(m)))
        high = n*(1+k*(1.04/math.sqrt(m)))

        num_inliers = values[(values >= low) & (values <= high)].size
        print(f"Ratio for k={k} is: {(num_inliers/1000):.6f}")
