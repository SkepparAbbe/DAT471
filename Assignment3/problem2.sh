#!/bin/bash

## SLURM commands 

# Job Info
#SBATCH --job-name=problem2

# Output file
#SBATCH --output=logs/problem2_%j.log

# Time limit to prioritize us more
#SBATCH --time=30

# Limit number cores
#SBATCH -c 64

DATASET=$"/mnt/planets.csv"

apptainer exec --bind /data/courses/2026_dat471_dit066/datasets/sc2/:/mnt/ /data/courses/2026_dat471_dit066/containers/assignment3.sif \
    bash -c "cat $DATASET | python3 assignment3_problem2.py -r local --num-cores 64 -k 10 | tee /dev/tty"