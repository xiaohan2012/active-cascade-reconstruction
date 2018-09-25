#! /bin/zsh

kernprof -l generate_queries.py \
	 -g lattice-100 \
	 -w \
	 -f ' ' \
	 -q entropy \
	 -n 5 \
	 -s 100 \
	 -p 0.00 \
	 -m simulation \
	 -r true_root \
	 -c cascade-weighted/lattice-100-msi-s0.25-o0.25-omuniform \
	 -d outputs/queries/test/ \
	 --verbose --debug
