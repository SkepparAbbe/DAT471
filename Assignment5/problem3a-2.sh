#!/bin/bash

## SLURM commands 

# Job Info
#SBATCH --job-name=problem3a-2

# Output file
#SBATCH --output=logs/problem3a-2_%j.log

# Time limit
#SBATCH --time=30

# Request max cores for the sweep
#SBATCH -c 64

DATASET=$"/mnt/huge"

apptainer exec --bind /data/courses/2026_dat471_dit066/datasets/gutenberg/:/mnt/ \
    /data/courses/2026_dat471_dit066/containers/assignment5.sif \
    python3 assignment5_problem3_skeleton.py -s 0x9747b28c -m 1024 -w 64 $DATASET