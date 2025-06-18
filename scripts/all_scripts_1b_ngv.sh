#!/usr/bin/env bash

DEEPDATA=/results
L_MODELS=(best_mcc best_precision best_recall)
CURRENT_DIR=$PWD
DATASET=(TATA nonTATA)
DATASET2=(dataset10k dataset40k)
DATASET2_CAT=(pa na pi ni)
DO_DEEP=0

# random datasets
for s in "${L_MODELS[@]}";
do
  if [[ $DO_DEEP = 1 ]];
  then
  for d in "${DATASET[@]}";
  do
#    python3 $CURRENT_DIR/script_1b.py results/hs_ngv_${d}_${s}_out.txt -c 0  \
#    -o results/DeePromoter_hs_ngv_${d}_${s}_out_metric_1.txt

    python3 $CURRENT_DIR/script_1b.py results/mm_ngv_${d}_${s}_out.txt -c 0  \
    -o results/DeePromoter_mm_ngv_${d}_${s}_out_metric_1.txt


  done
  else
  for d in "${DATASET2[@]}";
  do
    for f in "${DATASET2_CAT[@]}";
    do
      python3 $CURRENT_DIR/script_1b.py results/${d}_${f}_ngv_${s}_out.txt -c 0  \
      -o results/DeePromoter_${d}_${f}_ngv_${s}_out_metric_1.txt
    done
  done
  fi

done
