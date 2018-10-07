#! /bin/zsh

ROOT_DIR=/experiment

graphs=("email-univ")
sample_method="simulation"

inf_method="inf-probas"

query_dirname=${ROOT_DIR}/outputs/queries
cascade_dirname=${ROOT_DIR}/cascades
inf_dirname=${ROOT_DIR}/outputs/inference
fig_dirname=${ROOT_DIR}/outputs/figs

cascade_model="si"
cascade_fractions=(0.025)  #  0.25
obs_methods=("uniform")
n_queries=15
obs_fractions=(0.1)

eval_methods=(ap l1)

every=3

# other_params="${other_params} --use_cache"
# other_params="${other_params} --eval_with_mask"


query_dir_ids='random, pagerank, entropy, cond-entropy'
inf_dir_ids='random, pagerank, entropy, cond-entropy'
labels='random, pagerank, entropy, cond-entropy'


for graph in ${graphs}; do
    for eval_method in ${eval_methods}; do
	for cascade_fraction in ${cascade_fractions}; do
	    for obs_fraction in ${obs_fractions}; do
		for obs_method in ${obs_methods}; do
		    dataset_id="${graph}-m${cascade_model}-s${cascade_fraction}-o${obs_fraction}-om${obs_method}"

		    python3 eval_and_plot_performance.py \
			-g ${graph} \
			-d ${dataset_id} \
			-e ${eval_method} \
			-c ${cascade_dirname} \
			--query_dirname ${query_dirname} \
			--inf_dirname ${inf_dirname} \
			-s ${sample_method} \
			-n ${n_queries} \
			--query_dir_ids ${query_dir_ids} \
			--inf_dir_ids ${inf_dir_ids} \
			--legend_labels ${labels} \
			-f ${dataset_id} \
			--every ${every} \
			--fig_dirname ${fig_dirname} \
			--plot_step 1 \
			--check \
			--show_legend

		done
	    done
	done
    done
done


