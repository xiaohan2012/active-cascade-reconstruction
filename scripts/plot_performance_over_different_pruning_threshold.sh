#! /bin/zsh

graph="grqc"
sample_method=loop_erased
query_method=prediction_error
inf_method="inf_probas"

cascade_model="si"
stop_fraction=0.16
obs_fraction=0.1

dataset_id="${graph}-m${cascade_model}-s${stop_fraction}-o${obs_fraction}"

query_method="prediction_error"
n_queries=100

query_methods="prediction_error-p${min_proba}"

min_probas=(0.05 0.1 0.15 0.20 0.25)
query_methods="${query_method},${query_method}-p0.05,${query_method}-p0.1,${query_method}-p0.15,${query_method}-p0.20,${query_method}-p0.25"
labels="no pruning,0.05,0.1,0.15,0.20,0.25"

python3 plot_average_precision_score.py \
	-g ${graph} \
	-c ${dataset_id} \
	-s ${sample_method} \
	-i ${inf_method} \
	-n ${n_queries} \
        -q "${query_methods}" \
	-l ${labels} \
	-f pruning_thresholds

