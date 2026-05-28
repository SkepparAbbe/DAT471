#!/bin/bash

for i in 2 4 5; do
    for dataset in glove_small glove_large pubs; do
        sbatch "slurm_problem${i}/problem${i}b_${dataset}.sh"
    done
done