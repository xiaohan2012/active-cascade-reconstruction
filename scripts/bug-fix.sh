#! /bin/zsh

python3 generate_queries.py \
	-g lattice-1024 \
	-q entropy \
	-n 100 \
	-s 250 \
	-m loop_erased \
	-c cascade/bug-fix/ \
	-d outputs/queries/test \
	--debug --verbose
