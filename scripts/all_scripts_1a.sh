#!/usr/bin/env bash

DEEPDATA=data
DEEPROMOTE_MODELS=DeePromoter/output/
L_MODELS=(best_mcc best_precision best_recall)
CURRENT_DIR=$PWD
DATASET=(dataset10k dataset40k human_TATA human_nonTATA mouse_TATA mouse_nonTATA)
L_MODELS=(0 1 2)
for s in "${L_MODELS[@]}";
do
  for d in "${DATASET[@]}";
  do
    for f in ${DEEPDATA}/${d}/*ngv*.txt;
    do

    python3 script_1a.py $DEEPROMOTE_MODELS $f -t $s

    done

  done

done