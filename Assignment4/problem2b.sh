#!/bin/bash

## SLURM commands 

# Job Info
#SBATCH --job-name=problem2b

# Output file
#SBATCH --output=logs/problem2b_%j.log

# Time limit
#SBATCH --time=30

# Request max cores for the sweep
#SBATCH -c 64

DATASET=$"/mnt/climate_large.csv"
CSV_OUT="results_problem2b_$(date +%Y%m%d_%H%M%S).csv"

# Core counts to sweep — adjust as needed
CORE_COUNTS=(1 2 4 8 16 32 64)

for CORES in "${CORE_COUNTS[@]}"; do
    echo "--- Running with $CORES core(s) ---"
    apptainer exec \
        --bind /data/courses/2026_dat471_dit066/datasets/climate/:/mnt/ \
        /data/courses/2026_dat471_dit066/containers/assignment4.sif \
        python3 measure_2b.py \
            -w $CORES \
            --csv-out $CSV_OUT \
            $DATASET
done

echo "Results written to $CSV_OUT"