#!/bin/bash
#SBATCH --job-name=tuning_
#SBATCH --output=logs/tuning_%j.log

DATASET=$"/mnt/$1/"
SCRIPT=$"assignment2_problem2f.py"

echo "workers,batch,total_time,seq_time,par_time,par_fraction,checksum"  # header

for w in {0..6}; do
    for i in {0..10}; do
        for run in {1..3}; do
            apptainer exec --bind /data/courses/2026_dat471_dit066/datasets/gutenberg/:/mnt/ \
                /data/courses/2026_dat471_dit066/containers/assignment1.sif \
                python3 $SCRIPT -w $((2**w)) -b $((2**i)) $DATASET
        done
    done
done