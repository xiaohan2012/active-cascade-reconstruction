#! /bin/zsh

python3 query_one_round.py \
	-g lattice-100 \
	-f ' ' \
	-q entropy \
	-n 3 \
	-s 100 \
	-p 0.00 \
	-m simulation \
	-r true_root \
	--dataset lattice-100-msi-s0.25-o0.25-omuniform \
	-c /experiment/cascades/lattice-100-msi-s0.25-o0.25-omuniform/1.pkl \
	--verbose --debug \
	--infection_proba 0.5 \
	--cascade_size 0.25 \
	--cascade_model "si"
