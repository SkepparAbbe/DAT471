#!/bin/bash

## SLURM commands 

# Job Info
#SBATCH --job-name=problem3b

# Output file
#SBATCH --output=logs/problem3b_%j.log

# Time limit
#SBATCH --time=30

# Request max cores for the sweep
#SBATCH -c 64

DATASET=$"/mnt/big"
CSV_OUT="results_problem3b_$(date +%Y%m%d_%H%M%S).csv"

# Core counts to sweep — adjust as needed
CORE_COUNTS=(1 2 4 8 16 32 64)

for CORES in "${CORE_COUNTS[@]}"; do
    echo "--- Running with $CORES core(s) ---"
    apptainer exec --bind /data/courses/2026_dat471_dit066/datasets/gutenberg/:/mnt/ \
        /data/courses/2026_dat471_dit066/containers/assignment5.sif \
        python3 problem3b.py -s 0x9747b28c -m 1024 -w $CORES --csv-out $CSV_OUT $DATASET
done

echo "Results written to $CSV_OUT"