#! /bin/zsh

graph="grqc"
sample_method=loop_erased

cascade_model="ic"
obs_fraction=0.1

cascade_dirname="cascade-weighted"
query_dirname="queries-weighted"
query_dir_ids="random, pagerank, entropy-unweighted, entropy, prediction_error-unweighted, prediction_error"

inf_dirname="inf_probas-weighted"
inf_dir_ids="random, pagerank, entropy-unweighted, entropy, prediction_error-unweighted, prediction_error"

labels="random, pagerank, ent-unw, ent, prederror-unw, prederror"
data_id="${graph}-m${cascade_model}-o${obs_fraction}"

# query_methods="random, pagerank, entropy, prediction_error, entropy-unweighted, prediction_error-unweighted"
# labels="random, pagerank, entropy-w, prediction_error-w, entropy-u, prediction_error-u"
# data_id="${graph}-m${cascade_model}-o${obs_fraction}"
# print "${data_id}"
n_queries=100

python3 plot_average_precision_score.py \
	-g ${graph} \
	-d ${data_id} \
	-c ${cascade_dirname} \
	--query_dirname ${query_dirname} \
	--inf_dirname ${inf_dirname} \
	-s ${sample_method} \
	-n ${n_queries} \
        --query_dir_ids ${query_dir_ids} \
	--inf_dir_ids ${inf_dir_ids} \
	--legend_labels ${labels} \
        -f "${data_id}-query-with-weights-or-not"
