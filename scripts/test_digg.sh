#! /bin/zsh

python3 generate_queries.py \
	-g digg \
	-q entropy  \
	-n 100 \
	-s 100 \
	-m loop_erased \
	-c cascade/digg/9 \
	-d outputs/queries/digg/9/entropy \
	--debug --verbose
