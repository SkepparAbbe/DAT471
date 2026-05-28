#!/bin/bash

## SLURM commands 

# Job Info
#SBATCH --job-name=problem2b_glove_small

# Output file
#SBATCH --output=logs/problem2/problem2b_glove_small_%j.log

# Time limit to prioritize us more
#SBATCH --time=30

# Limit number cores
#SBATCH -c 64

# Request GPU
#SBATCH --gres=gpu:L40s:1

DATASET="/mnt/glove.6B.50d.txt"
QUERY_FILE="/mnt/glove.6B.50d_queries_"

# Define the batch sizes you want to test
BATCH_SIZES=(16 32 64 128 256 512)
QUERY_SIZES=("tiny" "small" "medium" "big")

for BATCH in "${BATCH_SIZES[@]}"; do
    for QUERY in "${QUERY_SIZES[@]}"; do
        echo "=================================================================================================="
        echo "Starting run with Batch Size: $BATCH On Dataset: $DATASET With query size: $QUERY" 
        echo "=================================================================================================="
        
        apptainer exec --nv --bind /data/courses/2026_dat471_dit066/datasets/glove/:/mnt/ /data/courses/2026_dat471_dit066/containers/assignment7.sif \
            python3 problem2a.py -d $DATASET -q "${QUERY_FILE}${QUERY}.txt" -l "${QUERY_FILE}${QUERY}_names.txt" -b $BATCH
            
        echo -e "\n" # Add a little spacing in the log between runs
    done
done