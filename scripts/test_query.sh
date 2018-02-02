#! /bin/zsh

python3 generate_queries.py \
	-g p2p \
	-q prediction_error \
	-n 5 \
	-s 250 \
	-p 0.00 \
	-m loop_erased \
	-r pagerank \
	-c cascade/p2p-msi-s0.04-o0.1/ \
	-d outputs/queries/test/ \
	--verbose --debug
