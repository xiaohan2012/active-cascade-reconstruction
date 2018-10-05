#! /bin/zsh

DATA_DIR=/experiment

if [ -d $DATA_DIR/outputs/queries/test/ ]; then
    rm -rf $DATA_DIR/outputs/queries/test/
fi

python3 generate_queries.py \
	-g infectious \
	-f '_0.5' \
	-q entropy \
	-n 3 \
	-s 100 \
	-p 0.00 \
	-m simulation \
	-r true_root \
	-c $DATA_DIR/cascades/infectious-msi-s0.1-o0.1-omuniform \
	-d $DATA_DIR/outputs/queries/test/ \
	--verbose --debug \
	--infection_proba 0.5 \
	--cascade_size 0.1 \
	--cascade_model "si"
