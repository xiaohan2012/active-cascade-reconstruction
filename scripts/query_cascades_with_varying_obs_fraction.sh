#! /bin/zsh

graph="nethept"
graph_suffix="_reversed"
cascade_fraction=0.02
n_samples=2500
sample_method=loop_erased
cascade_model="ic"
root_sampler='true_root'
query_methods=(random pagerank entropy prediction_error)
n_queries=10
obs_fractions=(0.1 0.2 0.3 0.4 0.5)

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
		-s ${n_samples} \
		-p ${min_proba} \
		-m ${sample_method} \
		-c ${cascade_dir} \
		-d outputs/queries-weighted/${dataset_id}/${sample_method}/${query_method}	
    done
done
