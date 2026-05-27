#!/bin/bash

## SLURM commands 

# Job Info
#SBATCH --job-name=problem1a

# Output file
#SBATCH --output=logs/problem1a_%j.log

# Time limit to prioritize us more
#SBATCH --time=30

# Limit number cores
#SBATCH -c 64

DATASET=$"/mnt/glove.6B.50d.txt"
QUERY_FILE=$"/mnt/glove.6B.50d_queries_small.txt"
LABELS=$"/mnt/glove.6B.50d_queries_small_names.txt"

apptainer exec --bind /data/courses/2026_dat471_dit066/datasets/glove/:/mnt/ /data/courses/2026_dat471_dit066/containers/assignment7.sif \
    python3 problem1a.py -d $DATASET -q $QUERY_FILE -l $LABELS -b 32