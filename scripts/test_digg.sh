#! /bin/zsh

kernprof -l generate_queries.py \
	 -g digg \
	 -q entropy  \
	 -n 2 \
	 -s 10 \
	 -m loop_erased \
	 -c cascade/digg/9 \
	 -d outputs/queries/digg/9/entropy \
	 -r earliest_obs \
	 --debug --verbose
