#!/bin/bash

for i in 2; do
    for dataset in glove_small glove_large pubs; do
        files=( logs/problem${i}/problem${i}b_${dataset}*.log )
        if [[ -e ${files[0]} ]]; then
            bash parse_results.sh "${files[@]}"
        else
            echo "No files matched for problem${i}, ${dataset}"
        fi
    done
done