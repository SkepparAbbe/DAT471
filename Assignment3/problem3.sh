#!/bin/bash

## SLURM commands 

# Job Info
#SBATCH --job-name=problem3

# Output file
#SBATCH --output=logs/problem3_%j.log

# Time limit to prioritize us more
# SBATCH --time=30

# Limit number cores
# SBATCH -c 64



DATASET=$"/mnt/twitter-2010_100k.txt"


apptainer exec --bind /data/courses/2026_dat471_dit066/datasets/twitter/:/mnt/ /data/courses/2026_dat471_dit066/containers/assignment3.sif \
    bash -c "cat $DATASET | python3 mrjob_twitter_follows.py -r local --num-cores 64| tee /dev/tty"