#!/bin/bash

## SLURM commands 

# Job Info
#SBATCH --job-name=problem1a

# Output file
#SBATCH --output=logs/problem1a_%j.log
#SBATCH --error=logs/problem1a_%j.log

# Time limit to prioritize us more
#SBATCH --time=5

# Limit number cores
#SBATCH -c 16

PASS=0
FAIL=0

RUN="apptainer exec /data/courses/2026_dat471_dit066/containers/assignment5.sif python3 assignment5_problem1_skeleton.py"

check() {
    local key="$1"
    local seed="$2"
    local expected="$3"

    # First run: let all output flow freely to the log
    $RUN --seed "$seed" "$key"

    # Second run: capture just the hash for comparison
    actual=$($RUN --seed "$seed" "$key" 2>/dev/null | awk '{print $1}')

    if [ "$actual" = "$expected" ]; then
        echo "PASS  seed=$seed  expected=$expected  key=\"$key\""
        ((PASS++))
    else
        echo "FAIL  seed=$seed  expected=$expected  got=$actual  key=\"$key\""
        ((FAIL++))
    fi
}

# empty string
check ""                                                            0x00000000  0x00000000
check ""                                                            0x00000001  0x514e28b7
check ""                                                            0xffffffff  0x81f16f39

# test
check "test"                                                        0x00000000  0xba6bd213
check "test"                                                        0x9747b28c  0x704b81dc

# Hello, world!
check "Hello, world!"                                               0x00000000  0xc0363e43
check "Hello, world!"                                               0x9747b28c  0x24884cba

# The quick brown fox
check "The quick brown fox jumps over the lazy dog"                 0x00000000  0x2e4ff723
check "The quick brown fox jumps over the lazy dog"                 0x9747b28c  0x2fa826cd

# Slovak
check "Rýchla hnedá líška preskočila lenivého psa"                 0x00000000  0x678b9be9
check "Rýchla hnedá líška preskočila lenivého psa"                 0x9747b28c  0x8d3382a7

# Russian
check "Быстрая коричневая лиса перепрыгивает через ленивую собаку" 0x00000000  0xa94f1f75
check "Быстрая коричневая лиса перепрыгивает через ленивую собаку" 0x9747b28c  0x4152021b

# Chinese
check "敏捷的棕色狐狸跳过了懒狗"                                     0x00000000  0x6687dfe4
check "敏捷的棕色狐狸跳过了懒狗"                                     0x9747b28c  0xc7df48f1

echo ""
echo "Results: $PASS passed, $FAIL failed"