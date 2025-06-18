#!/usr/bin/env bash

DEEPDATA=/results
L_MODELS=(best_mcc best_precision best_recall)
CURRENT_DIR=$PWD
DATASET=(10k 40k)
for s in "${L_MODELS[@]}";
do
  for d in "${DATASET[@]}";
  do
    python3 $CURRENT_DIR/script_1b.py results/dataset${d}_na_${s}_out.txt results/dataset${d}_pa_${s}_out.txt \
    results/dataset${d}_ni_${s}_out.txt results/dataset${d}_pi_${s}_out.txt -c 0 1 0 1 \
    -o results/DeePromoter_dataset${d}_${s}_out_metric_1.txt
    python3 $CURRENT_DIR/script_1b.py results/dataset${d}_na_${s}_out.txt results/dataset${d}_pa_${s}_out.txt \
    results/dataset${d}_ni_${s}_out.txt results/dataset${d}_pi_${s}_out.txt -c 1 1 1 1 \
    -o results/DeePromoter_dataset${d}_${s}_out_metric_2.txt
    python3 $CURRENT_DIR/script_1c.py results/dataset${d}_na_${s}_out_score.txt results/dataset${d}_pa_${s}_out_score.txt \
    results/dataset${d}_ni_${s}_out_score.txt results/dataset${d}_pi_${s}_out_score.txt -c 0 1 0 1 \
    -o results/DeePromoter_dataset${d}_${s}_out_AUC_1.txt

  done
  python3 $CURRENT_DIR/script_1b.py results/dataset10k_na_${s}_out.txt results/dataset10k_pa_${s}_out.txt \
  results/dataset10k_ni_${s}_out.txt results/dataset10k_pi_${s}_out.txt \
  results/dataset40k_na_${s}_out.txt results/dataset40k_pa_${s}_out.txt \
  results/dataset40k_ni_${s}_out.txt results/dataset40k_pi_${s}_out.txt \
  -c 0 1 0 1 0 1 0 1 \
  -o results/DeePromoter_dataset50k_${s}_out_metric_1.txt
  python3 $CURRENT_DIR/script_1b.py results/dataset10k_na_${s}_out.txt results/dataset10k_pa_${s}_out.txt \
  results/dataset10k_ni_${s}_out.txt results/dataset10k_pi_${s}_out.txt \
  results/dataset40k_na_${s}_out.txt results/dataset40k_pa_${s}_out.txt \
  results/dataset40k_ni_${s}_out.txt results/dataset40k_pi_${s}_out.txt \
  -c 1 1 1 1 1 1 1 1 \
  -o results/DeePromoter_dataset50k_${s}_out_metric_2.txt
  python3 $CURRENT_DIR/script_1c.py results/dataset10k_na_${s}_out_score.txt results/dataset10k_pa_${s}_out_score.txt \
  results/dataset10k_ni_${s}_out_score.txt results/dataset10k_pi_${s}_out_score.txt \
  results/dataset40k_na_${s}_out_score.txt results/dataset40k_pa_${s}_out_score.txt \
  results/dataset40k_ni_${s}_out_score.txt results/dataset40k_pi_${s}_out_score.txt \
  -c 0 1 0 1 0 1 0 1 \
  -o results/DeePromoter_dataset50k_${s}_out_AUC_1.txt
done