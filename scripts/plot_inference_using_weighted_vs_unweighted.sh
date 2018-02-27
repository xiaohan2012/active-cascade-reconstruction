#! /bin/zsh
# check the effects of weighting on inference algorithms
# assuming queries are made using edge weights

graph="grqc"
sample_method=loop_erased

cascade_model="ic"
obs_fraction=0.1
query_methods="random, random-weighted, prediction_error, prediction_error-weighted"
labels="random, random-w-inf, prediction_error, prediction_error-w-inf"
data_id="${graph}-m${cascade_model}-o${obs_fraction}"
# print "${data_id}"
n_queries=100

python3 plot_average_precision_score.py \
	-g ${graph} \
	-d ${data_id} \
	-c cascade-weighted \
	--query_dirname queries-weighted \
	-i inf_probas-unweighted \
	-s ${sample_method} \
	-n ${n_queries} \
        -q ${query_methods} \
	--legend_labels ${labels} \
        -f "${data_id}-inference-using-weights"


