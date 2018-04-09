#! /bin/zsh

graph="lattice-1024"
sample_method=loop_erased

inf_method="inf_probas"

query_dirname='queries-weighted'
cascade_dirname='cascade-weighted'
inf_dirname='inf_probas-weighted'

cascade_model="si"
cascade_fraction="0.02"
# cascade_fractions=(0.01 0.02 0.04 0.08 0.16 0.32)
# cascade_fractions=(0.04 0.08 0.16 0.32 0.64)
# cascade_fractions=(0.02 0.04 0.08 0.16 0.32)
# 0.2 0.3 0.4 0.5
# 0.2 0.3 0.4 0.5
obs_fractions=(0.1 0.2 0.3 0.4 0.5)



# eval_method="ap"
# other_params="--eval_with_mask"

# eval_method="precision_at_cascade_size"

eval_method="auc"
other_params="--eval_with_mask"


# query_dir_ids="random, pagerank, entropy, prediction_error, weighted_prediction_error"
# inf_dir_ids="random, pagerank, entropy, prediction_error, weighted_prediction_error"
# labels="random, pagerank, entropy, prederror, weighted_prederror"

query_dir_ids="random, pagerank, entropy, prediction_error"
inf_dir_ids="random, pagerank, entropy, prediction_error"
labels="random, pagerank, entropy, prederror"


n_queries=10

for obs_fraction in ${obs_fractions}; do
    dataset_id="${graph}-m${cascade_model}-s${cascade_fraction}-o${obs_fraction}"

    print "
python3 plot_average_precision_score.py \
	-g ${graph} \
	-d ${dataset_id} \
        -e ${eval_method} \
        ${other_params} \
	-c ${cascade_dirname} \
	--query_dirname ${query_dirname} \
	--inf_dirname ${inf_dirname} \
	-s ${sample_method} \
	-n ${n_queries} \
        --query_dir_ids \"${query_dir_ids}\" \
	--inf_dir_ids \"${inf_dir_ids}\" \
	--legend_labels \"${labels}\" \
        -f \"${dataset_id}\"
"

done