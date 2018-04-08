#! /bin/zsh

graph="lattice-1024"
graph_suffix="_reversed"
cascade_fraction=0.02
n_tree_samples=2500
sample_method=loop_erased
cascade_model="ic"
root_sampler='true_root'
query_methods=(random pagerank entropy prediction_error weighted_prediction_error)
n_queries=10
obs_fractions=(0.1 0.2 0.3 0.4 0.5)

inf_method="inf_probas"

min_proba=0.05

for obs_fraction in ${obs_fractions}; do
    dataset_id="${graph}-m${cascade_model}-s${cascade_fraction}-o${obs_fraction}"

    cascade_dir="cascade-weighted/${dataset_id}"
    for query_method in ${query_methods}; do
	print "${query_method} on ${cascade_dir}"
	python3 generate_queries.py \
		-g ${graph} \
		-f ${graph_suffix} \
		--root_sampler ${root_sampler} \
		--weighted \
		-q ${query_method} \
		-n ${n_queries} \
		-s ${n_tree_samples} \
		-p ${min_proba} \
		-m ${sample_method} \
		-c ${cascade_dir} \
		-d outputs/queries-weighted/${dataset_id}/${sample_method}/${query_method}

	python3 infer_from_queries.py \
		-g ${graph} \
		-f ${graph_suffix} \
		--weighted \
		-s ${n_tree_samples} \
		--sampling_method ${sample_method} \
		-m ${inf_method} \
		-c ${cascade_dir} \
		--query_method ${query_method} \
		--root_sampler ${root_sampler} \
		-q outputs/queries-weighted/${dataset_id}/${sample_method}/${query_method} \
		-p outputs/${inf_method}-weighted/${dataset_id}/${sample_method}/${query_method}	
    done
done
