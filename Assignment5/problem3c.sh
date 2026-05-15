#!/bin/bash

## SLURM commands 

# Job Info
#SBATCH --job-name=problem3c

# Output file
#SBATCH --output=logs/problem3c_%j.log

# Time limit
#SBATCH --time=30

# Request max cores for the sweep
#SBATCH -c 64

DATASET=$"/mnt/small"

apptainer exec --bind /data/courses/2026_dat471_dit066/datasets/gutenberg/:/mnt/ \
    /data/courses/2026_dat471_dit066/containers/assignment5.sif \
    python3 problem3c.py -m 1024 -w 64 $DATASET