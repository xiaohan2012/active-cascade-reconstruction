#! /bin/bash

python3 infer_from_queries.py \
	-g grqc \
	-s 250 \
	-m order-steiner-tree \
	-c cascade/grqc/ \
	-q outputs/queries/grqc/cut \
	-p outputs/test \
	--debug
