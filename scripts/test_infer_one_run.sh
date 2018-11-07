#! /bin/zsh

python3 infer_one_round.py \
	-g lattice-100 \
	-f " " \
	--dataset lattice-100-mic-s0.25-o0.25-omuniform \
	-c /experiment/cascades/lattice-100-mic-s0.25-o0.25-omuniform/1.pkl \
	--inference_n_samples 100 \
	--inference_sampling_method mst \
	--query_method entropy \
	--n_queries 3 \
	--query_sampling_method mst \
	--root_sampler true_root \
	--query_n_samples 100 \
	--min_proba 0.0\
	--verbose 1 \
	--debug \
	--infection_proba 0.5 \
	--cascade_size 0.25 \
        --cascade_model "ic" \
	--infer_every 1
