#!/bin/bash

## SLURM commands 

# Job Info
#SBATCH --job-name=problem1b

# Output file
#SBATCH --output=logs/problem1b_%j.log

# Time limit to prioritize us more
#SBATCH --time=30

# RAM allocation

# Limit number cores
#SBATCH -c 64

DATASET="/mnt/glove.6B.50d.txt"
QUERY_FILE="/mnt/glove.6B.50d_queries_small.txt"
LABELS="/mnt/glove.6B.50d_queries_small_names.txt"

# Define the batch sizes you want to test
BATCH_SIZES=(0 16 32 64 128 256 512)

for BATCH in "${BATCH_SIZES[@]}"; do
    echo "=========================================================="
    echo "Starting run with Batch Size: $BATCH"
    echo "=========================================================="
    
    apptainer exec --bind /data/courses/2026_dat471_dit066/datasets/glove/:/mnt/ /data/courses/2026_dat471_dit066/containers/assignment7.sif \
        python3 problem1b.py -d $DATASET -q $QUERY_FILE -l $LABELS -b $BATCH
        
    echo -e "\n" # Add a little spacing in the log between runs
done