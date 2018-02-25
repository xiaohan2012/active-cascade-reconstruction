#! /bin/zsh

python3 generate_queries.py \
	-g grqc \
	-w \
	-q prediction_error \
	-n 5 \
	-s 250 \
	-p 0.00 \
	-m loop_erased \
	-r pagerank \
	-c cascade-weighted/grqc-mic-o0.1/ \
	-d outputs/queries/test/ \
	--verbose --debug
