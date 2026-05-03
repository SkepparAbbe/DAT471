#!/bin/bash

## SLURM commands 

# Job Info
#SBATCH --job-name=problem4c

# Output file
#SBATCH --output=logs/problem4c_%j.log

# Time limit
#SBATCH --time=30

# Request max cores for the sweep
#SBATCH -c 32

DATASET="/mnt/twitter-2010_10M.txt"
CSV_OUT="results_problem4_$(date +%Y%m%d_%H%M%S).csv"

# Core counts to sweep — adjust as needed
CORE_COUNTS=(1 2 4 8 16 32)

for CORES in "${CORE_COUNTS[@]}"; do
    echo "--- Running with $CORES core(s) ---"
    apptainer exec \
        --bind /data/courses/2026_dat471_dit066/datasets/twitter/:/mnt/ \
        /data/courses/2026_dat471_dit066/containers/assignment3.sif \
        bash -c "python3 mrjob_twitter_measure_problem4.py \
            --num-workers $CORES \
            --csv-out $CSV_OUT \
            $DATASET"
done

echo "Results written to $CSV_OUT"