#! /bin/zsh

python3  generate_queries.py \
	 -g karate \
	 -q prediction_error \
	 -n 2 \
	 -s 10 \
	 -m cut \
	 -c cascade/karate/ \
	 -d outputs/queries/karate \
	 --debug
