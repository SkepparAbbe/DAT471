import argparse
import struct
import matplotlib.pyplot as plt
import numpy as np
from assignment5_problem1_skeleton import murmur3_32

def number_collisions(n):
    return (n*(n-1))/2

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Computes statistical properties for MurMurHash3'
    )
    parser.add_argument('-d','--dataset',help='dataset of keys to be hashed',type=str)
    args = parser.parse_args()
    print(args.dataset)

    seed = 0xee418b6c
    frequency = [0] * 128
    values = []

    with open(args.dataset) as f:
        for line in f:
            key = line.strip()
            h = murmur3_32(key,seed)
            bits = h & 0x7F
            frequency[bits] += 1
            values.append(bits)
    frequency = np.array(frequency)
    values = np.array(values)

    plt.bar(range(128), frequency, width=1.0, edgecolor='steelblue', linewidth=0.5)
    plt.xlabel("Hash bucket (7 LSBs)")
    plt.ylabel("Frequency")
    plt.savefig('problem1b_frequency.png')
    plt.show()

    mean = np.mean(values)
    std = np.std(values)

    print(f"The arithmetic mean of the hash values is: {mean}")
    print(f"The standard deviation of the hash values is: {std}")
    print("-"*20)

    num_keys = np.sum(frequency)
    num_key_pairs = number_collisions(num_keys)
    clashes = frequency[frequency > 1]
    number_of_collisions = np.sum(number_collisions(clashes))
    collision_probability = number_of_collisions / num_key_pairs

    print(f"The collision probability is approximately: {collision_probability}")
