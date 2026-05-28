#!/bin/bash

# Usage: ./parse_results.sh <logfile> [output.csv]
# Extracts benchmark metrics from SLURM job logs

LOG_FILE="${1:-}"

if [[ -z "$LOG_FILE" || ! -f "$LOG_FILE" ]]; then
    echo "Usage: $0 <logfile>" >&2
    exit 1
fi

CSV_FILE="${LOG_FILE%.log}_results.csv"  # strips .log, appends _results.csv

# Write CSV header
echo "dataset,query_size,batch_size,num_queries,total_time_s,per_query_time_s,host_to_gpu_s,device_to_cpu_s,errors" > "$CSV_FILE"

# ── Column widths ──────────────────────────────────────────────────
W_DS=20; W_QS=8; W_BS=7; W_NT=7; W_TT=10; W_TQ=12; W_TG=12; W_TC=12; W_ERR=7

print_sep() {
    printf '+-%*s-+-%*s-+-%*s-+-%*s-+-%*s-+-%*s-+-%*s-+-%*s-+-%*s-+\n' \
        $W_DS '' $W_QS '' $W_BS '' $W_NT '' $W_TT '' $W_TQ '' $W_TG '' $W_TC '' $W_ERR '' \
        | tr ' ' '-'
}

print_header() {
    printf '| %-*s | %-*s | %-*s | %-*s | %-*s | %-*s | %-*s | %-*s | %-*s |\n' \
        $W_DS "Dataset" \
        $W_QS "Q.Size" \
        $W_BS "Batch" \
        $W_NT "#Queries" \
        $W_TT "Total(s)" \
        $W_TQ "Per Query(s)" \
        $W_TG "→GPU(s)" \
        $W_TC "←CPU(s)" \
        $W_ERR "Errors"
}

echo ""
echo "========== Benchmark Results =========="
echo ""
print_sep
print_header
print_sep

# ── Parse ──────────────────────────────────────────────────────────
dataset=""; query_size=""; batch_size=""
n_queries=""; total_time=""; to_gpu=""; to_cpu=""; errors=""

flush_row() {
    [[ -z "$dataset" || -z "$batch_size" ]] && return

    per_query=""
    if [[ -n "$n_queries" && -n "$total_time" && "$n_queries" -gt 0 ]]; then
        per_query=$(awk "BEGIN { printf \"%.6f\", $total_time / $n_queries }")
    fi

    ds_short=$(basename "$dataset")

    fmt6() { [[ "$1" == "N/A" || -z "$1" ]] && echo "N/A" || awk "BEGIN{printf \"%.6f\",$1}"; }
    tt=$(fmt6 "$total_time"); tg=$(fmt6 "$to_gpu"); tc=$(fmt6 "$to_cpu")

    # ── Print table row ──
    printf '| %-*s | %-*s | %-*s | %-*s | %-*s | %-*s | %-*s | %-*s | %-*s |\n' \
        $W_DS "${ds_short:0:$W_DS}" \
        $W_QS "${query_size:-N/A}" \
        $W_BS "${batch_size:-N/A}" \
        $W_NT "${n_queries:-N/A}" \
        $W_TT "$tt" \
        $W_TQ "${per_query:-N/A}" \
        $W_TG "$tg" \
        $W_TC "$tc" \
        $W_ERR "${errors:-N/A}"

    # ── Append CSV row ──
    printf '%s,%s,%s,%s,%s,%s,%s,%s,%s\n' \
        "$ds_short" \
        "${query_size:-N/A}" \
        "${batch_size:-N/A}" \
        "${n_queries:-N/A}" \
        "$tt" \
        "${per_query:-N/A}" \
        "$tg" \
        "$tc" \
        "${errors:-N/A}" \
        >> "$CSV_FILE"

    dataset=""; query_size=""; batch_size=""
    n_queries=""; total_time=""; to_gpu=""; to_cpu=""; errors=""
}

while IFS= read -r line; do
    if [[ "$line" =~ ^Starting\ run\ with\ Batch\ Size:\ ([0-9]+)\ On\ Dataset:\ (.+)\ With\ query\ size:\ (.+)$ ]]; then
        flush_row
        batch_size="${BASH_REMATCH[1]}"
        dataset="${BASH_REMATCH[2]}"
        query_size="${BASH_REMATCH[3]}"

    elif [[ "$line" =~ Performing\ ([0-9]+)\ NN\ queries\ took\ ([0-9.]+) ]]; then
        n_queries="${BASH_REMATCH[1]}"
        total_time="${BASH_REMATCH[2]}"

    elif [[ "$line" =~ Transferring\ data\ to\ GPU\ took\ ([0-9.]+) ]]; then
        to_gpu="${BASH_REMATCH[1]}"

    elif [[ "$line" =~ Transferring\ data\ to\ CPU\ took\ ([0-9.]+) ]]; then
        to_cpu="${BASH_REMATCH[1]}"

    elif [[ "$line" =~ Number\ of\ erroneous\ queries:\ ([0-9]+) ]]; then
        errors="${BASH_REMATCH[1]}"

    elif [[ "$line" =~ Batch\ size\ used\ \(b=([0-9]+)\) && -z "$batch_size" ]]; then
        batch_size="${BASH_REMATCH[1]}"
    fi
done < "$LOG_FILE"

flush_row

print_sep
echo ""
echo "Columns: Dataset | Query Size | Batch | #Queries | Total time (s) |"
echo "         Per-query time (s) | Host→GPU (s) | Device→CPU (s) | Errors"
echo ""
echo "CSV saved to: $CSV_FILE"
echo ""