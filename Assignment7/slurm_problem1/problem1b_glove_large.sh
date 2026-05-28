#!/bin/bash

## SLURM commands 

# Job Info
#SBATCH --job-name=problem1b_glove_large

# Output file
#SBATCH --output=logs/problem1b_glove_large_%j.log

# Time limit to prioritize us more
#SBATCH --time=30

# RAM allocation
#SBATCH --mem 64

# Limit number cores
#SBATCH -c 64


DATASET="/mnt/glove.840B.300d.txt"
QUERY_FILE="/mnt/glove.840B.300d_queries_"

# Define the batch sizes you want to test
BATCH_SIZES=(0 16 32 64 128 256 512)
QUERY_SIZES=("tiny" "small" "medium" "big")

for BATCH in "${BATCH_SIZES[@]}"; do
    for QUERY in "${QUERY_SIZES[@]}"; do
        echo "=================================================================================================="
        echo "Starting run with Batch Size: $BATCH On Dataset: $DATASET With query size: $QUERY" 
        echo "=================================================================================================="
        
        apptainer exec --nv --bind /data/courses/2026_dat471_dit066/datasets/glove/:/mnt/ /data/courses/2026_dat471_dit066/containers/assignment7.sif \
            python3 problem1b.py -d $DATASET -q "${QUERY_FILE}${QUERY}.txt" -l "${QUERY_FILE}${QUERY}_names.txt" -b $BATCH
            
        echo -e "\n" # Add a little spacing in the log between runs
    done
done