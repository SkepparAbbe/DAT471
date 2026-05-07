#!/bin/bash

## SLURM commands 

# Job Info
#SBATCH --job-name=problem2a

# Output file
#SBATCH --output=logs/problem2a_%j.log

# Time limit to prioritize us more
#SBATCH --time=4

# Limit number cores
#SBATCH -c 16

DATASET=$"/mnt/climate_small.csv"

apptainer exec --bind /data/courses/2026_dat471_dit066/datasets/climate/:/mnt/ /data/courses/2026_dat471_dit066/containers/assignment4.sif \
    python3 pyspark_climate.py -w 64 $DATASET