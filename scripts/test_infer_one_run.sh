#! /bin/zsh

QUERY_DIR=outputs/queries/test
OUTPUT_DIR=outputs/inference/test

if [ -d ${OUTPUT_DIR} ]; then
    rm -rf  ${OUTPUT_DIR}
fi

python3 infer_one_round.py \
	-g lattice-100 \
	-f " " \
	-s 10 \
	--sampling_method "simulation" \
	--query_method entropy \
	-c cascade-weighted/lattice-100-msi-s0.25-o0.25-omuniform/1.pkl \
	-q $QUERY_DIR \
	-p $OUTPUT_DIR \
	--verbose --debug \
	--infection_proba 0.5 \
	--cascade_size 0.25 \
        --cascade_model "si"       

if [ -f $OUTPUT_DIR/1.pkl ]; then
    print 'SUCCESS'
    print "output is produced at $OUTPUT_DIR/1.pkl"
fi
