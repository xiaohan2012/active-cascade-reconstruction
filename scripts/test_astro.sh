#! /bin/zsh

kernprof -l generate_queries.py \
	 -g astro \
	 -q prediction_error \
	 -n 10 \
	 -s 100 \
	 -m loop_erased \
	 -c cascade/astro/ \
	 -d outputs/queries/astro-test/ \
	 --debug --verbose

