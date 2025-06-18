#!/usr/bin/env bash

DEEPDATA=/results
L_MODELS=(best_mcc best_precision best_recall)
CURRENT_DIR=$PWD
DATASET=(10k 40k)

# random datasets
for s in "${L_MODELS[@]}";
do
  for d in "${DATASET[@]}";
  do
    python3 $CURRENT_DIR/script_1b.py results/random${d}_${s}_out.txt -c 0  \
    -o results/DeePromoter_random${d}_${s}_out_metric_1.txt


  done
  python3 $CURRENT_DIR/script_1b.py results/random10k_${s}_out.txt results/random40k_${s}_out.txt -c 0 0 \
  -o results/DeePromoter_random50k_${s}_out_metric_1.txt

done