#!/bin/bash

## SLURM commands 

# Job Info
#SBATCH --job-name=problem2c

# Output file
#SBATCH --output=logs/problem2c_%j.log

# Time limit to prioritize us more
#SBATCH --time=30

DATASET=$"/mnt/$1/"

echo $DATASET

apptainer exec --bind /data/courses/2026_dat471_dit066/datasets/gutenberg/:/mnt/ /data/courses/2026_dat471_dit066/containers/assignment1.sif python3 $2 $DATASET