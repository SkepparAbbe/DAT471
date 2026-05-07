#!/bin/bash

## SLURM commands 

# Job Info
#SBATCH --job-name=problem1c

# Output file
#SBATCH --output=logs/problem1c_%j.log

# Time limit to prioritize us more
#SBATCH --time=30

# Limit number cores
#SBATCH -c 64

DATASET=$"/mnt/twitter-2010_10k.txt"

apptainer exec --bind /data/courses/2026_dat471_dit066/datasets/twitter/:/mnt/ /data/courses/2026_dat471_dit066/containers/assignment4.sif \
    python3 pyspark_twitter_followers.py -w 64 $DATASET