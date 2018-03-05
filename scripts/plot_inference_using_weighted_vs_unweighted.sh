#! /bin/zsh
# check the effects of weighting on inference algorithms
# assuming queries are made using edge weights

graph="lattice-1024"
sample_method=loop_erased

cascade_model="ic"
obs_fraction=0.1

cascade_dirname="cascade-weighted"
query_dirname="queries-weighted"
query_dir_ids="random, random, prediction_error, prediction_error"

inf_dirname="inf_probas-unweighted"
inf_dir_ids="random, random-weighted, prediction_error, prediction_error-weighted"

labels="random-unw-inf, random-w-inf, prederr-unw-inf, prederr-w-inf"

if [ ${cascade_model} = "ic" ]; then    
    dataset_id="${graph}-m${cascade_model}-o${obs_fraction}"
else
    dataset_id="${graph}-m${cascade_model}-s${stop_fraction}-o${obs_fraction}"
fi

# dataset_id="${graph}-m${cascade_model}-o${obs_fraction}"
# print "${dataset_id}"
n_queries=100

python3 plot_average_precision_score.py \
	-g ${graph} \
	-d ${dataset_id} \
	-c ${cascade_dirname} \
	--query_dirname ${query_dirname} \
	--inf_dirname ${inf_dirname} \
	-s ${sample_method} \
	-n ${n_queries} \
        --query_dir_ids ${query_dir_ids} \
	--inf_dir_ids ${inf_dir_ids} \
	--legend_labels ${labels} \
        -f "${dataset_id}-inference-with-weights-or-not"


