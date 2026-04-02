#!/bin/bash
echo "Kernel Version: $(uname -v)"
echo "Python interpreter version: $(python3 --version | awk '{print $NF}')"
echo "CPU $(lscpu | grep "Model name" | tr -s ' ')"
EOF | apptainer exec /data/courses/2026_dat471_dit066/containers/assignment1.sif bash command.sh
