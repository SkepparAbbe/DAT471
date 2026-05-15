#!/bin/bash

## SLURM commands 

# Job Info
#SBATCH --job-name=problem3a

# Output file
#SBATCH --output=logs/problem3a_%j.log
#SBATCH --error=logs/problem3a_%j.log

# Time limit to prioritize us more
#SBATCH --time=2

# Limit number cores
#SBATCH -c 64

datasets=("tiny" "small" "medium")
seeds=("0x9747b28c" "0xc40376f3")
ms=(16 256 32768)

declare -A expected
expected["tiny,0x9747b28c,16"]=67814.2
expected["tiny,0xc40376f3,16"]=40909.7
expected["tiny,0x9747b28c,256"]=46694.7
expected["tiny,0xc40376f3,256"]=48169.3
expected["tiny,0x9747b28c,32768"]=47163.3
expected["tiny,0xc40376f3,32768"]=47494.0
expected["small,0x9747b28c,16"]=440627.0
expected["small,0xc40376f3,16"]=230393.2
expected["small,0x9747b28c,256"]=305543.4
expected["small,0xc40376f3,256"]=286945.9
expected["small,0x9747b28c,32768"]=285573.8
expected["small,0xc40376f3,32768"]=282263.8
expected["medium,0x9747b28c,16"]=1766817.2
expected["medium,0xc40376f3,16"]=1400442.3
expected["medium,0x9747b28c,256"]=1776137.9
expected["medium,0xc40376f3,256"]=1803475.3
expected["medium,0x9747b28c,32768"]=1743068.2
expected["medium,0xc40376f3,32768"]=1741231.4

for dataset in "${datasets[@]}"; do
    for seed in "${seeds[@]}"; do
        for m in "${ms[@]}"; do
            DATASET="/mnt/${dataset}/"
            key="${dataset},${seed},${m}"
            echo "=== dataset=$dataset seed=$seed m=$m ==="
            echo "Expected: ${expected[$key]}"
            apptainer exec --bind /data/courses/2026_dat471_dit066/datasets/gutenberg/:/mnt/ \
                /data/courses/2026_dat471_dit066/containers/assignment5.sif \
                python3 assignment5_problem3_skeleton.py -s $seed -m $m -w 64 $DATASET 2>/dev/null
            echo "---"
        done
    done
done