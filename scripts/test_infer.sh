#! /bin/bash

python3 infer_from_queries.py \
	-g lattice-1024 \
	-s 250 \
	-m inf_probas \
	-c cascade/bug-fix/ \
	--query_method pagerank \
	-q outputs/queries/lattice-1024-msi-s0.04-o0.1/loop_erased \
	-p outputs/test \
	--verbose --debug



