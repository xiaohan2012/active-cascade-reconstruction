#! /bin/zsh

kernprof -l generate_queries.py \
		 -g grqc \
		 -q prediction_error \
		 -n 2 \
		 -s 10 \
		 -m cut \
		 -c cascade/grqc-s0.2-o0.1/ \
		 -d outputs/queries/grqc-s0.2-o0.1/ \
		 --debug
