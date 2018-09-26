#! /bin/bash

rm outputs/inf_probas/test/*

python3 infer_from_queries.py \
	-g lattice-100 \
	-f " " \
	-s 10 \
	--sampling_method "simulation" \
	-c cascade-weighted/lattice-100-msi-s0.25-o0.25-omuniform \
	--query_method entropy \
	-q outputs/queries/test/ \
	-p outputs/inf_probas/test \
	--verbose --debug \
	--infection_proba 0.5 \
	--cascade_size 0.5 \
        --cascade_model "si"
	



