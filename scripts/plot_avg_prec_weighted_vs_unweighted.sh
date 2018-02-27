#! /bin/zsh

graph="grqc"
sample_method=loop_erased

cascade_model="ic"
obs_fraction=0.1
query_methods="random, pagerank, entropy, prediction_error, entropy-unweighted, prediction_error-unweighted"
labels="random, pagerank, entropy-w, prediction_error-w, entropy-u, prediction_error-u"
data_id="${graph}-m${cascade_model}-o${obs_fraction}"
# print "${data_id}"
n_queries=100

python3 plot_average_precision_score.py \
	-g ${graph} \
	-d ${data_id} \
	-c cascade-weighted \
	--query_dirname queries-weighted \
	-i inf_probas-weighted \
	-s ${sample_method} \
	-n ${n_queries} \
        -q ${query_methods} \
	--legend_labels ${labels} \
        -f ${data_id}


