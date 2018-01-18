#! /bin/zsh

python3 infer_from_queries.py \
	-g grqc \
	-s 250 \
	-c cascade/grqc/ \
	-q outputs/queries/grqc/loop_erased/ \
	-p outputs/inf_probas/grqc/loop_erased
