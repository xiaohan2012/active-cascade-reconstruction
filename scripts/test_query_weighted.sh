#! /bin/zsh

kernprof -l generate_queries.py \
	-g grqc \
	-f _s0.03 \
	-w \
	-q prediction_error \
	-n 5 \
	-s 250 \
	-p 0.00 \
	-m loop_erased \
	-r pagerank \
	--root_pagerank_noise 0.5 \
	-c cascade-weighted/grqc-mic-s0.03-o0.1/ \
	-d outputs/queries/test/ \
	--verbose --debug \
	--incremental_cascade
