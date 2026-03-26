#!/bin/bash

## SLURM commands 

# Job Info
#SBATCH --job-name=problem2_apptainer

# Output file
#SBATCH --output=logs_problem2/job_python%j.log

DATASET=$"/data/courses/2026_dat471_dit066/datasets/bike_sharing_hourly.csv"
PYTHON_SCRIPT=$"/opt/mystery.py"

# cat $DATASET

apptainer exec /data/courses/2026_dat471_dit066/containers/assignment1.sif cat $DATASET