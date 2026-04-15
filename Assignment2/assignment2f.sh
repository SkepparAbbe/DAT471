#!/bin/bash

## SLURM commands 

# Job Info
#SBATCH --job-name=problem2f

# Output file
#SBATCH --output=logs/problem2f_%j.log

DATASET=$"/mnt/$1/"
SCRIPT=$"assignment2_problem2f.py"

echo $DATASET

for i in {0..6}; do
    apptainer exec --bind /data/courses/2026_dat471_dit066/datasets/gutenberg/:/mnt/ /data/courses/2026_dat471_dit066/containers/assignment1.sif python3 $SCRIPT -w $((2**i)) -b $2 $DATASET
done
#for i in {0..7}; do
#    echo "Batch size: $((2**i))\n"
#    apptainer exec --bind /data/courses/2026_dat471_dit066/datasets/gutenberg/:/mnt/ /data/courses/2026_dat471_dit066/containers/assignment1.sif python3 $SCRIPT -w 64 -b $((2**i)) $DATASET
#done
