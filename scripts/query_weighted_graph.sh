#! /bin/zsh

graph="grqc"
graph_suffix="_preprocessed"
obs_fraction="leaves"
cascade_fraction=0.02

sample_method=cut
cascade_model="ic"
root_sampler='true_root'
query_methods=(random pagerank entropy prediction_error)

min_proba=0.1

n_queries=10


dataset_id="${graph}-m${cascade_model}-s${cascade_fraction}-o${obs_fraction}"

cascade_dir="cascade-weighted/${dataset_id}"

print "dataset_id: ${dataset_id}"

# without incremental sampling
for query_method in ${query_methods}; do
    print "${query_method} on ${cascade_dir}"
    python3 generate_queries.py \
	    -g ${graph} \
	    -f ${graph_suffix} \
	    --root_sampler ${root_sampler} \
	    --weighted \
	    -q ${query_method} \
	    -n ${n_queries} \
	    -s 250 \
	    -p ${min_proba} \
	    -m ${sample_method} \
	    -c ${cascade_dir} \
	    -d outputs/queries-weighted/${dataset_id}/${sample_method}/${query_method}
done
