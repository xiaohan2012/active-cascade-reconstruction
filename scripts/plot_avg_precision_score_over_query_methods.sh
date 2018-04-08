#! /bin/zsh

graph="grqc"
sample_method=loop_erased

inf_method="inf_probas"

query_dirname='queries-weighted'
cascade_dirname='cascade-weighted'
inf_dirname='inf_probas-weighted'

cascade_model="ic"
cascade_fraction=0.02
# cascade_fractions=(0.01 0.02 0.04 0.08 0.16 0.32)
# cascade_fractions=(0.04 0.08 0.16 0.32 0.64)
# cascade_fractions=(0.02 0.04 0.08 0.16 0.32)
obs_fractions=(0.1)


eval_method="ap"
eval_with_mask=True

# eval_method="precision_at_cascade_size"
# eval_with_mask=False

# query_dir_ids="random, pagerank, entropy, entropy-inc, prediction_error, prediction_error-inc"
# inf_dir_ids="random, pagerank, entropy, entropy-inc, prediction_error, prediction_error-inc"
# labels="random, pagerank, entropy, entropy-inc, prediction_error, prederr-inc"

query_dir_ids="random, pagerank, entropy, prediction_error"
inf_dir_ids="random, pagerank, entropy, prediction_error"
labels="random, pagerank, entropy, prediction_error"

n_queries=10

for obs_fraction in ${obs_fractions}; do
    dataset_id="${graph}-m${cascade_model}-s${cascade_fraction}-o${obs_fraction}"
    # print "${data_id}"

    # if (( ${cascade_fraction} == 0.01 )); then
    # 	n_queries=20
    # elif (( ${cascade_fraction} == 0.02 )); then
    # 	n_queries=30
    # elif (( ${cascade_fraction} == 0.04 )); then
    # 	n_queries=45
    # elif (( ${cascade_fraction} == 0.08 )); then
    # 	n_queries=60
    # else
    # 	n_queries=100
    # fi
    print "
python3 plot_average_precision_score.py \
	-g ${graph} \
	-d ${dataset_id} \
        -e ${eval_method} \
        --eval_with_mask ${eval_with_mask} \
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
