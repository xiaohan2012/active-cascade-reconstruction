#! /bin/zsh

kernprof -l generate_queries.py \
	 -g grqc \
	 -w \
	 -f '_reversed' \
	 -q entropy \
	 -n 5 \
	 -s 100 \
	 -p 0.00 \
	 -m simulation \
	 -r true_root \
	 -c cascade/grqc-msi-s0.02-o0.1/ \
	 -d outputs/queries/test/ \
	 --verbose --debug
