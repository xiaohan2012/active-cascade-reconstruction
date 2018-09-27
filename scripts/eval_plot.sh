#! /bin/zsh

# graphs=("grqc" "p2p" "lattice-1024" "infectious")
# graphs=("grqc" "p2p")
# graphs=("lattice-1024-sto" "infectious-sto")
# graphs=("grqc-sto")
graphs=("lattice-100")
sample_method="simulation"

inf_method="inf-probas"

query_dirname='queries-weighted'
cascade_dirname='cascade-weighted'
inf_dirname="${inf_method}-weighted"

cascade_model="si"
cascade_fractions=(0.25)  #  0.25
obs_methods=("uniform")
# "bfs-head"  "uniform"
n_queries=100
# cascade_fractions=(0.01 0.02 0.04 0.08 0.16 0.32)
# cascade_fractions=(0.04 0.08 0.16 0.32 0.64)
# cascade_fractions=(0.02 0.04 0.08 0.16 0.32)
# 0.2 0.3 0.4 0.5
# 0.2 0.3 0.4 0.5
obs_fractions=(0.25)

# eval_methods=(l1 l2)
eval_methods=(ap)
# eval_methods=("p@k" entropy mrr ap)
# eval_methods=(l1 l2 cross_entropy)
# eval_methods=("n")
# l1 l2
# eval_methods=(cross_entropy)
every=1
# eval_method="ap"
# eval_method="p_at_hidden"
# eval_method="entropy"
# eval_method="map"
# eval_method='mrr'


other_params="--plot_step=1"
# other_params="${other_params} --use_cache"
other_params="${other_params} --eval_with_mask"
other_params="${other_params} --check"
other_params="${other_params} --show_legend"



query_dir_ids="random, pagerank, entropy, cond-entropy"
inf_dir_ids="random, pagerank, entropy, cond-entropy"
labels="random, pagerank, entropy, cond-entropy"

# query_dir_ids="pagerank"
# inf_dir_ids="pagerank"
# labels="pagerank"



for graph in ${graphs}; do
    for eval_method in ${eval_methods}; do
	for cascade_fraction in ${cascade_fractions}; do
	    for obs_fraction in ${obs_fractions}; do
		for obs_method in ${obs_methods}; do
		dataset_id="${graph}-m${cascade_model}-s${cascade_fraction}-o${obs_fraction}-om${obs_method}"

		print "
python3 eval_and_plot_performance.py \
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


