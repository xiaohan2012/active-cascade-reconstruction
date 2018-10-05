#! /bin/bash

DATA_DIR=/experiment

if [ -d $DATA_DIR/outputs/inference/test/ ]; then
    rm -rf $DATA_DIR/outputs/inference/test/
fi

python3 infer_from_queries.py \
    -g infectious \
    -f '_0.5' \
    -s 10 \
    --sampling_method "simulation" \
    -c /experiment/cascades/infectious-msi-s0.1-o0.1-omuniform \
    --query_method entropy \
    -q $DATA_DIR/outputs/queries/test/ \
    -p $DATA_DIR/outputs/inference/test \
    --root_sampler true_root \
    --verbose --debug \
    --infection_proba 0.5 \
    --cascade_size 0.1 \
    --cascade_model "si"




