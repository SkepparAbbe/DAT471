#!/bin/bash

## SLURM commands 

# Job Info
#SBATCH --job-name=problem2c

# Output file
#SBATCH --output=logs_problem2/problem2c%j.log

DATASET=$"data/courses/2026 dat471 dit066/datasets/gutenberg/$1"

apptainer exec /data/courses/2026_dat471_dit066/containers/assignment1.sif $2 $DATASET