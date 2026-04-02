#!/bin/bash

## SLURM commands 

# Job Info
#SBATCH --job-name=problem2c_apptainer

# Output file
#SBATCH --output=logs_problem2/problem2c_apptainer%j.log

# Time limit to prioritize us more
#SBATCH --time=4

DATASET=$"/mnt/courses/2026_dat471_dit066/datasets/bike_sharing_hourly.csv"
PYTHON_SCRIPT=$"assignment1_problem2c.py"

apptainer exec --bind /data/:/mnt /data/courses/2026_dat471_dit066/containers/assignment1.sif python3 $PYTHON_SCRIPT $DATASET