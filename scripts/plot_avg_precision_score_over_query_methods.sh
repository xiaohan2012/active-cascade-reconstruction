#! /bin/zsh

graph="grqc"
sample_method=cut

inf_method="inf_probas"

query_dirname='queries-weighted'
cascade_dirname='cascade-weighted'
inf_dirname='inf_probas-weighted'

cascade_model="ic"
# stop_fractions=(0.01 0.02 0.04 0.08 0.16 0.32)
# stop_fractions=(0.04 0.08 0.16 0.32 0.64)
# stop_fractions=(0.02 0.04 0.08 0.16 0.32)
stop_fractions=(0.03)
obs_fraction=0.5

eval_method="auc"
query_dir_ids="random, pagerank, entropy, prediction_error"
inf_dir_ids="random, pagerank, entropy, prediction_error"
labels="random, pagerank, entropy, prederror"

n_queries=30

for stop_fraction in ${stop_fractions}; do
    dataset_id="${graph}-m${cascade_model}-s${stop_fraction}-o${obs_fraction}"
    # print "${data_id}"

    # if (( ${stop_fraction} == 0.01 )); then
    # 	n_queries=20
    # elif (( ${stop_fraction} == 0.02 )); then
    # 	n_queries=30
    # elif (( ${stop_fraction} == 0.04 )); then
    # 	n_queries=45
    # elif (( ${stop_fraction} == 0.08 )); then
    # 	n_queries=60
    # else
    # 	n_queries=100
    # fi
    print "
python3 plot_average_precision_score.py \
	-g ${graph} \
	-d ${dataset_id} \
        -e ${eval_method} \
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
