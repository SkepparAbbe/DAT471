#!/bin/bash

## SLURM commands 

# Job Info
#SBATCH --job-name=computer_info_script

# Output file
#SBATCH --output=logs/job_%j.log

## Script
# Get the necessary information
CPU_INFO=$(lscpu)
GPU_COUNT=$(nvidia-smi --query-gpu=name --format=csv,noheader | wc -l)

findIn() {
    echo "$1" | grep "^\s*$2" 
}

trimResult() {
    tr -s ' '
}

# CPU information
findIn "$CPU_INFO" "Model name" | trimResult
SOCKETS=$(findIn "$CPU_INFO" "Socket(s)" | awk '{print $NF}')
NR_OF_CORES_PER_SOCKET=$(findIn "$CPU_INFO" "Core(s) per socket:" | awk '{print $NF}')

echo -n "Physical CPUs: "; echo "$SOCKETS"
echo -n "Hardware threads: "; findIn "$CPU_INFO" "CPU(s):" | awk '{print $NF}'
echo "Number of cores: $((SOCKETS*NR_OF_CORES_PER_SOCKET))"

CPU_FREQUENCIES=$(cat /proc/cpuinfo | grep "cpu MHz" | awk '{print $NF}' | sort)
echo -n "CPU Max MHz: "; echo "$CPU_FREQUENCIES" | head -1
echo -n "CPU Min MHz: "; echo "$CPU_FREQUENCIES" | tail -1

findIn "$CPU_INFO" "'Core(s) per socket" | trimResult
findIn "$CPU_INFO" "L1i" | trimResult
echo -e -n "\tCache line length: "; getconf LEVEL1_ICACHE_LINESIZE
findIn "$CPU_INFO" "L1d" | trimResult
echo -e -n "\tCache line length: "; getconf LEVEL1_DCACHE_LINESIZE
findIn "$CPU_INFO" "L2" | trimResult
echo -e -n "\tCache line length: "; getconf LEVEL2_CACHE_LINESIZE
findIn "$CPU_INFO" "L3" | trimResult
echo -e -n "\tCache line length: "; getconf LEVEL3_CACHE_LINESIZE
findIn "$CPU_INFO" "Architecture" | trimResult

## Memory information
echo -n "Total Memory: "; cat /proc/meminfo | grep "MemTotal" | awk '{print $(NF-1) " " $NF}'

# GPU Info
echo "GPU(s): $GPU_COUNT"
for i in $(seq 0 $((GPU_COUNT - 1))); do
    echo "--- GPU $i ---"
    echo -n "GPU model: "; nvidia-smi --query-gpu=name --format=csv,noheader -i $i
    echo -n "GPU memory: "; nvidia-smi --query-gpu=memory.total --format=csv,noheader -i $i
done

# The file system of /data
echo -n "File system of /data: "; df -T /data | awk 'NR==2 {print $2}'
USED_STORAGE=$(df -T /data | awk 'NR==2 {print $4}')
AVAILABLE_STORAGE=$(df -T /data | awk 'NR==2 {print $4}')
echo "Free storage on /data: $AVAILABLE_STORAGE"
echo "Total storage on /data: $((AVAILABLE_STORAGE + USED_STORAGE))"


# Kernel / Linux Info
echo -n "Kernel Release: "; uname -r
echo -n "Kernel Version: "; uname -v
echo -n "GNU/Linux distribution: "; lsb_release -a | grep "Description:" | awk '{print $(NF-2) " " $(NF-1) " " $NF}'

# Python3 Info
echo "Python 3 interpreter (filename): $(which python3) (version $(python3 --version | awk '{print $NF}'))"