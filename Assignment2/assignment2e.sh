#!/bin/bash

## SLURM commands 

# Job Info
#SBATCH --job-name=problem2e

# Output file
#SBATCH --output=logs/problem2e_%j.log

## Time limit to prioritize us more
##SBATCH --time=30

DATASET=$"/mnt/$1/"
SCRIPT=$"assignment2_problem2e.py"

echo $DATASET

for i in {0..6}; do
    apptainer exec --bind /data/courses/2026_dat471_dit066/datasets/gutenberg/:/mnt/ /data/courses/2026_dat471_dit066/containers/assignment1.sif python3 $SCRIPT -w $((2**i)) $DATASET
done