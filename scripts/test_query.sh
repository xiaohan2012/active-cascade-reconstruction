#! /bin/zsh

kernprof -l generate_queries.py \
	 -g lattice-100 \
	 -f ' ' \
	 -q entropy \
	 -n 3 \
	 -s 100 \
	 -p 0.00 \
	 -m simulation \
	 -r true_root \
	 -c cascade-weighted/lattice-100-msi-s0.25-o0.25-omuniform \
	 -d outputs/queries/test/ \
	 --verbose --debug \
	 --infection_proba 0.5 \
	 --cascade_size 0.5 \ 
	 --cascade_model "si"
