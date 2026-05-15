#!/usr/bin/env python3

import argparse
import struct

def rol32(x,k):
    """Auxiliary function (left rotation for 32-bit words)"""
    return ((x << k) | (x >> (32-k))) & 0xffffffff

def murmur3_32(key, seed):
    """Computes the 32-bit murmur3 hash"""
    key_bytes = key.encode("utf-8")
    
    C1 = 0xcc9e2d51
    C2 = 0x1b873593

    h = seed
    length = len(key_bytes)

    num_blocks = length >> 2
    for i in range(num_blocks):
        k = struct.unpack_from("<I", key_bytes, i*4)[0]

        # Scramble
        k = (k * C1) & 0xFFFFFFFF
        k = rol32(k, 15)
        k = (k * C2) & 0xFFFFFFFF

        # Accumulation into hash
        h ^= k;
        h = rol32(h, 13);
        h = (h * 5 + 0xe6546b64) & 0xFFFFFFFF;

    # Tail calculation
    tail_offset = num_blocks * 4
    tail = key_bytes[tail_offset:]
    k = 0
    tail_len = length & 3  # length % 4
    if tail_len >= 3:
        k ^= tail[2] << 16
    if tail_len >= 2:
        k ^= tail[1] << 8
    if tail_len >= 1:
        k ^= tail[0]
        k  = (k * C1) & 0xFFFFFFFF
        k  = rol32(k, 15)
        k  = (k * C2) & 0xFFFFFFFF
        h ^= k

    # Finalization
    h ^= length
    h ^= h >> 16
    h  = (h * 0x85ebca6b) & 0xFFFFFFFF
    h ^= h >> 13
    h  = (h * 0xc2b2ae35) & 0xFFFFFFFF
    h ^= h >> 16

    return auto_int(hex(h))

def auto_int(x):
    """Auxiliary function to help convert e.g. hex integers"""
    return int(x,0)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Computes MurMurHash3 for the keys.'
    )
    parser.add_argument('key',nargs='*',help='key(s) to be hashed',type=str)
    parser.add_argument('-s','--seed',type=auto_int,default=0,help='seed value')
    args = parser.parse_args()

    seed = args.seed
    for key in args.key:
        h = murmur3_32(key,seed)
        print(f'{h:#010x}\t{key}')
        