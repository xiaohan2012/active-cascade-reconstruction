#! /bin/zsh

OUTPUT_DIR=outputs/queries/test/
if [ -d ${OUTPUT_DIR} ]; then
    rm -rf  ${OUTPUT_DIR}
fi

python3 query_one_round.py \
	-g lattice-100 \
	-f ' ' \
	-q entropy \
	-n 3 \
	-s 100 \
	-p 0.00 \
	-m simulation \
	-r true_root \
	-c cascade-weighted/lattice-100-msi-s0.25-o0.25-omuniform/1.pkl \
	-d ${OUTPUT_DIR} \
	--verbose --debug \
	--infection_proba 0.5 \
	--cascade_size 0.25 \
	--cascade_model "si"

if [ -f $OUTPUT_DIR/1.pkl ]; then
    print 'SUCCESS'
    print "output is produced at $OUTPUT_DIR/1.pkl"
fi
