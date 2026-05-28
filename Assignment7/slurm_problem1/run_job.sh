#!/bin/bash

#SBATCH --job-name=glove_bench
#SBATCH --time=00:30:00
#SBATCH --mem=64G
#SBATCH -c 64


BATCH=$1
QUERY=$2

DATASET="/mnt/glove.840B.300d.txt"
QUERY_FILE="/mnt/glove.840B.300d_queries_${QUERY}.txt"
NAMES_FILE="/mnt/glove.840B.300d_queries_${QUERY}_names.txt"

echo "=================================================================================================="
echo "Starting SLURM Job ID: $SLURM_JOB_ID"
echo "Batch Size: $BATCH | Query Size: $QUERY" 
echo "=================================================================================================="

apptainer exec --nv --bind /data/courses/2026_dat471_dit066/datasets/glove/:/mnt/ \
    /data/courses/2026_dat471_dit066/containers/assignment7.sif \
    python3 problem1b.py -d "$DATASET" -q "$QUERY_FILE" -l "$NAMES_FILE" -b "$BATCH"