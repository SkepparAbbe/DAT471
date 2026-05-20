#!/usr/bin/env python3

import argparse
import sys
import os
from pyspark import SparkContext, SparkConf
import math
import string
import time
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
        
# Lazy 
def parse_file(file, seed, log2m):
    # return (compute_jr(w.strip(string.punctuation), seed, log2m) for w in file.split() if w.strip(string.punctuation))
    return (compute_jr(w, seed, log2m) for w in file.split())

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Using HyperLogLog, computes the approximate number of '
            'distinct words in all .txt files under the given path.'
    )
    parser.add_argument('path',help='path to walk',type=str)
    parser.add_argument('-s','--seed',type=auto_int,default=0,help='seed value')
    parser.add_argument('-m','--num-registers',type=int,required=True,
                            help=('number of registers (must be a power of two)'))
    parser.add_argument('-w','--num-workers',type=int,default=1,
                        help='number of Spark workers')
    args = parser.parse_args()

    seed = args.seed
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


    # Implement HyperLogLog here

    # pairs = data.flatMap(lambda x: parse_file(x, seed, log2m)) \
    #     .reduceByKey(lambda x,y: max(x,y)) \
    #     .
    
    # num_pairs = pairs.count()
    # num_zeros = m - num_pairs
    # n_hat = alpha(m) * m**2 * (1 / (pairs.map(lambda jr: 2**(-jr[1])).sum() + num_zeros))

    # if (n_hat <= ((5/2) * m)) and (num_zeros > 0):
    #     n_hat = m * math.log(m/num_zeros)
    # elif (n_hat > ((1/30) * 2**32)):
    #     n_hat = -2**32 * math.log(1-(n_hat / 2**32))

    num_pairs, harmonic_sum = data \
        .flatMap(lambda x: parse_file(x, seed, log2m)) \
        .reduceByKey(max) \
        .map(lambda jr: (1, 2**(-jr[1]))) \
        .reduce(lambda a, b: (a[0]+b[0], a[1]+b[1]))
    
    num_zeros = m - num_pairs
    n_hat = alpha(m) * m**2 * (1 / (harmonic_sum + num_zeros))

    if (n_hat <= ((5/2) * m)) and (num_zeros > 0):
        n_hat = m * math.log(m/num_zeros)
    elif (n_hat > ((1/30) * 2**32)):
        n_hat = -2**32 * math.log(1-(n_hat / 2**32))

    E = n_hat # replace with your own 
    
    end = time.time()

    print(f'Cardinality estimate: {E}')
    print(f'Number of workers: {num_workers}')
    print(f'Took {end-start} s')

    
    

    