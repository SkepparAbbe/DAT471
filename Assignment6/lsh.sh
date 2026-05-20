#!/bin/bash

## SLURM commands 

# Job Info
#SBATCH --job-name=problem4

# Output file
#SBATCH --output=logs/problem4_%j.log

# Time limit to prioritize us more
#SBATCH --time=5

# Limit number cores
#SBATCH -c 64

DATASET=$"/mnt/glove.840B.300d.txt"
#DATASET=$"/mnt/glove.6B.50d.txt"
QUERY_FILE=$"queries.txt"

apptainer exec --bind /data/courses/2026_dat471_dit066/datasets/glove/:/mnt/ /data/courses/2026_dat471_dit066/containers/assignment6.sif \
    python3 lsh_lsh.py -D 50 -k 20 -L 10 $DATASET $QUERY_FILE 