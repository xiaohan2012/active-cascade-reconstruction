#! /bin/zsh

# graphs=("grqc" "p2p" "lattice-1024" "infectious")
# graphs=("grqc" "p2p")
# graphs=("lattice-1024-sto" "infectious-sto")
# graphs=("grqc-sto")
graphs=("grqc-sto")
sample_method=loop_erased

inf_method="inf_probas"

query_dirname='queries-weighted'
cascade_dirname='cascade-weighted'
inf_dirname='inf_probas-weighted'

cascade_model="ic"
cascade_fractions=(0.025)  #  0.25
obs_methods=("uniform")
# "bfs-head"  "uniform"
n_queries=500
# cascade_fractions=(0.01 0.02 0.04 0.08 0.16 0.32)
# cascade_fractions=(0.04 0.08 0.16 0.32 0.64)
# cascade_fractions=(0.02 0.04 0.08 0.16 0.32)
# 0.2 0.3 0.4 0.5
# 0.2 0.3 0.4 0.5
obs_fractions=(0.2)

# eval_methods=(l1 l2)
eval_methods=(ap)
# eval_methods=("p@k" entropy mrr ap)
# eval_methods=(l1 l2 cross_entropy)
# eval_methods=("n")
# l1 l2
# eval_methods=(cross_entropy)
every=5
# eval_method="ap"
# eval_method="p_at_hidden"
# eval_method="entropy"
# eval_method="map"
# eval_method='mrr'


other_params="--plot_step=5"
# other_params="${other_params} --use_cache"
other_params="${other_params} --eval_with_mask"
other_params="${other_params} --check"

# eval_method="precision_at_cascade_size"

# eval_method="auc"
# other_params="${other_params} --eval_with_mask"
# other_params="${other_params} --use_cache"


# query_dir_ids="random, pagerank, entropy, prediction_error, weighted_prediction_error"
# inf_dir_ids="random, pagerank, entropy, prediction_error, weighted_prediction_error"
# labels="random, pagerank, entropy, prederror, weighted_prederror"

# query_dir_ids="entropy, prediction_error, mutual-info"
# inf_dir_ids="entropy, prediction_error, mutual-info"
# labels="entropy, prederror, mutual-info"

# query_dir_ids="random, pagerank, entropy, prediction_error, mutual-info"
# inf_dir_ids="random, pagerank, entropy, prediction_error, mutual-info"
# labels="random, pagerank, entropy, prederror, mutual-info"

query_dir_ids="random, pagerank, entropy, prediction_error, mutual-info, oracle-e, oracle-l"
inf_dir_ids="random, pagerank, entropy, prediction_error, mutual-info, oracle-e, oracle-l"
labels="random, pagerank, entropy, prederror, mutual-info, oracle-e, oracle-l"




for graph in ${graphs}; do
    for eval_method in ${eval_methods}; do
	for cascade_fraction in ${cascade_fractions}; do
	    for obs_fraction in ${obs_fractions}; do
		for obs_method in ${obs_methods}; do
		dataset_id="${graph}-m${cascade_model}-s${cascade_fraction}-o${obs_fraction}-om${obs_method}"

		print "
python3 plot_performance.py \
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
        -f \"${dataset_id}\" \
        --every ${every}
"


		done
	    done
	done
    done
done


