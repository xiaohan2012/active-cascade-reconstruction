#! /bin/zsh

python3 generate_queries.py \
	 -g grqc \
	 -q prediction_error \
	 -n 5 \
	 -s 10 \
	 -m cut \
	 -c cascade/grqc-s0.2-o0.1/ \
	 -d outputs/queries/grqc-s0.2-o0.1/test/
