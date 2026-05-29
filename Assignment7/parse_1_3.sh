#!/bin/bash

# Usage: ./parse_results.sh <input_directory>
INPUT_DIR="${1:-}"

if [[ -z "$INPUT_DIR" || ! -d "$INPUT_DIR" ]]; then
    echo "Usage: $0 <directory_with_logs>" >&2
    exit 1
fi

CSV_FILE="${INPUT_DIR%/}/combined_benchmark_results.csv"

# CSV header
echo "log_file,config,batch_size,num_queries,total_time_s,per_query_time_s,queries_per_s,errors" > "$CSV_FILE"

# ── Column widths for terminal presentation ────────────────────────
W_FILE=25; W_CFG=15; W_BS=7; W_NT=10; W_TT=12; W_TQ=15; W_QPS=15; W_ERR=7

print_sep() {
    printf '+-%*s-+-%*s-+-%*s-+-%*s-+-%*s-+-%*s-+-%*s-+-%*s-+\n' \
        $W_FILE '' $W_CFG '' $W_BS '' $W_NT '' $W_TT '' $W_TQ '' $W_QPS '' $W_ERR '' \
        | tr ' ' '-'
}

print_header() {
    printf '| %-*s | %-*s | %-*s | %-*s | %-*s | %-*s | %-*s | %-*s |\n' \
        $W_FILE "Log File" \
        $W_CFG "Config (B_Q)" \
        $W_BS "Batch" \
        $W_NT "#Queries" \
        $W_TT "Total(s)" \
        $W_TQ "Per Query(s)" \
        $W_QPS "Throughput" \
        $W_ERR "Errors"
}

echo ""
echo "========== Consolidated Benchmark Results =========="
echo ""
print_sep
print_header
print_sep

# ── Global Parsing Variables ───────────────────────────────────────
current_file=""
has_job=false
query_size=""; batch_size=""
n_queries=""; total_time=""; errors=""
status="OK"

flush_row() {
    if [ "$has_job" = false ]; then
        has_job=true
        return
    fi

    config_id="${batch_size:-N/A}_${query_size:-N/A}"
    file_short=$(basename "$current_file")

    # Determine what number to show for queries
    display_queries="$n_queries"
    
    if [[ -z "$display_queries" ]]; then
        # Map the string name to the actual size number if the job crashed
        case "${query_size,,}" in
            tiny)   display_queries="10" ;;
            small)  display_queries="100" ;;
            medium) display_queries="1000" ;; 
            big)    display_queries="10000" ;; 
            *)      display_queries="N/A" ;;
        esac
    fi

    per_query="N/A"
    qps="N/A"
    tt_display="N/A"

    # Determine what goes into the Total Time column
    if [[ "$status" != "OK" ]]; then
        tt_display="$status"
    elif [[ -n "$total_time" ]]; then
        tt_display=$(awk "BEGIN { printf \"%.6f\", $total_time }")
        
        # Calculate derived metrics if we have a valid numeric query count
        if [[ -n "$n_queries" && "$n_queries" =~ ^[0-9]+$ && "$n_queries" -gt 0 ]]; then
            per_query=$(awk "BEGIN { printf \"%.6f\", $total_time / $n_queries }")
            qps=$(awk "BEGIN { printf \"%.2f\", $n_queries / $total_time }")
        fi
    fi

    # ── Print table row ──
    printf '| %-*s | %-*s | %-*s | %-*s | %-*s | %-*s | %-*s | %-*s |\n' \
        $W_FILE "${file_short:0:$W_FILE}" \
        $W_CFG "${config_id:0:$W_CFG}" \
        $W_BS "${batch_size:-N/A}" \
        $W_NT "${display_queries:0:$W_NT}" \
        $W_TT "$tt_display" \
        $W_TQ "$per_query" \
        $W_QPS "$qps" \
        $W_ERR "${errors:-N/A}"

    # ── Append unified CSV row ──
    printf '%s,%s,%s,%s,%s,%s,%s,%s\n' \
        "$file_short" \
        "$config_id" \
        "${batch_size:-N/A}" \
        "$display_queries" \
        "$tt_display" \
        "$per_query" \
        "$qps" \
        "${errors:-N/A}" \
        >> "$CSV_FILE"

    # Reset metrics for next cycle
    n_queries=""; total_time=""; errors=""
    status="OK"
}

# Check if log files exist
shopt -s nullglob
log_files=("$INPUT_DIR"/*.log)
if [ ${#log_files[@]} -eq 0 ]; then
    echo "Error: No files ending in .log found in '$INPUT_DIR'" >&2
    print_sep
    exit 1
fi

# Loop through every log file discovered
for filepath in "${log_files[@]}"; do
    current_file="$filepath"
    has_job=false 
    batch_size="N/A"
    query_size="N/A"
    
    while IFS= read -r line; do
        if [[ "$line" =~ ^Starting\ SLURM\ Job\ ID: ]]; then
            if [ "$has_job" = true ]; then
                flush_row
            fi
            has_job=true

        elif [[ "$line" =~ ^Batch\ Size:\ ([0-9]+)\ \|\ Query\ Size:\ (.+) ]]; then
            batch_size="${BASH_REMATCH[1]}"
            query_size="${BASH_REMATCH[2]}"

        elif [[ "$line" =~ Performing\ ([0-9]+)\ NN\ queries\ took\ ([0-9.]+) ]]; then
            n_queries="${BASH_REMATCH[1]}"
            total_time="${BASH_REMATCH[2]}"

        elif [[ "$line" =~ Number\ of\ erroneous\ queries:\ ([0-9]+) ]]; then
            errors="${BASH_REMATCH[1]}"

        elif [[ "$line" =~ CANCELLED\ AT\ .*\ DUE\ TO\ TIME\ LIMIT ]]; then
            status="Timeout"

        elif [[ "$line" =~ Killed\ +apptainer\ exec ]]; then
            status="OOM"

        # NEW CHECK: Capture explicit Python/NumPy memory errors
        elif [[ "$line" =~ ArrayMemoryError ]]; then
            status="OOM"
        fi
    done < "$filepath"

    flush_row
done

print_sep
echo ""
echo "Consolidated CSV saved to: $CSV_FILE"
echo ""