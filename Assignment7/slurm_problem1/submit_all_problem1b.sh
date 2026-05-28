#!/bin/bash

BATCH_SIZES=(0 16 32 64 128 256 512)
QUERY_SIZES=("tiny" "small" "medium" "big")

mkdir -p logs

for BATCH in "${BATCH_SIZES[@]}"; do
    for QUERY in "${QUERY_SIZES[@]}"; do
        
        LOG_FILE="logs/glove_b${BATCH}_${QUERY}_%j.log"
        JOB_NAME="glove_${BATCH}_${QUERY}"
        
        echo "Submitting: $JOB_NAME -> $LOG_FILE"
        
        # Override the output file dynamically via the sbatch command
        sbatch --job-name="$JOB_NAME" --output="$LOG_FILE" run_job.sh "$BATCH" "$QUERY"
        
    done
done