#!/bin/bash

CURRENT_DIR=$PWD
LOG_FILE=$CURRENT_DIR/log.txt
DATA=data/
MODEL_DIR=models

# Function to print timestamped messages
function log_message() {
    local message="$1"
    local timestamp="$(date '+%Y-%m-%d %H:%M:%S')"
    local log_entry="$timestamp - $message"

    echo "$log_entry"
    echo "$log_entry" >> "$LOG_FILE"
}

# Function to run a command and save output to log
function run_and_log() {
    local cmd="$1"
    local action="$2"

    output=$($cmd 2>&1)
    status=$?

    echo "$output" | tee -a "$LOG_FILE"

    if [[ $status -ne 0 ]]; then
        log_message "Error: $action failed. Exiting."
        exit 1
    else
        log_message "$action completed successfully."
    fi
}


MODELS=("RegSeqNet_alt1_5_10k_1" \
    "RegSeqNet_alt2_5_10k_1" \
    "RegSeqNet_custom40_5_10k_3" \
    "RegSeqNet_custom41_5_10k_20" \
    "RegSeqNet_custom_4_40k_1" "RegSeqNet_custom_4_40k_3" \
    "RegSeqNet_custom_5_10k_22" "RegSeqNet_custom_5_10k_23" )
DATASET=(dataset10k ) # dataset40k
CATEGORY=(pa na pi ni pa_ngv na_ngv pi_ngv ni_ngv random)


for m in "${MODELS[@]}"
do
    FFLAG=""
    if [[ ${m} =~ '10k' ]]; then
        DATASET="dataset40k"
    fi
    if [[ ${m} =~ '40k' ]]; then
        DATASET="dataset10k"
    fi
    if [[ ${m} =~ '_5_' ]]; then
        FFLAG="-f"
    fi


    run_and_log "python3 $CURRENT_DIR/script_7.py $CURRENT_DIR/results/tmp/${DATASET}_pa_${m}_out.txt \
        $CURRENT_DIR/results/tmp/${DATASET}_na_${m}_out.txt \
        $CURRENT_DIR/results/tmp/${DATASET}_pi_${m}_out.txt \
        $CURRENT_DIR/results/tmp/${DATASET}_ni_${m}_out.txt \
        $CURRENT_DIR/results/tmp/${DATASET}_pa_ngv_${m}_out.txt \
        $CURRENT_DIR/results/tmp/${DATASET}_na_ngv_${m}_out.txt \
        $CURRENT_DIR/results/tmp/${DATASET}_pi_ngv_${m}_out.txt \
        $CURRENT_DIR/results/tmp/${DATASET}_ni_ngv_${m}_out.txt \
        $CURRENT_DIR/results/tmp/${DATASET}_random_${m}_out.txt \
        -o $CURRENT_DIR/results/RegSeqNet_new_count_out_${m}.csv $FFLAG" "compute metrics"
done