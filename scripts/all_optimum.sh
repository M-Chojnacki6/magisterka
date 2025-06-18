#!/bin/bash

CURRENT_DIR=$PWD
LOG_FILE=$CURRENT_DIR/log.txt
DATA=/data/
MODEL_DIR=/models

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


MODELS=("alt2") # "custom40" "custom41" "alt1" 
CATEGORY=(2)
IN_FILES=(C)

for d in "${IN_FILES[@]}";
do
    for t in "${CATEGORY[@]}"
	do
		for m in "${MODELS[@]}"
		do
			run_and_log "python3 $CURRENT_DIR/find_best_sequences.py $MODEL_DIR/${m}/${m}_last.model -n 1000 -i $DATA/${d}.fasta -c ${t} -o results/optim_${m}_${d}_${t}.fasta" "find optimal ${m}"
		done
	done

done

