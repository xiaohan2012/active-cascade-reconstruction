#! /bin/zsh

graph="grqc"
sample_method=cut
query_methods=(random pagerank entropy prediction_error)
sampling_based_query_methods=(entropy prediction_error)

cascade_model="ic"
obs_fraction=0.1
cascade_fraction=0.005
min_proba=0.00
graph_suffix="_s0.03"

n_queries=10
root_sampler='random'

dataset_id="${graph}-m${cascade_model}-s${cascade_fraction}-o${obs_fraction}"

cascade_dir="cascade-weighted/${dataset_id}"

print "dataset_id: ${dataset_id}"



# with incremental sampling
for query_method in ${sampling_based_query_methods}; do
    print "${query_method} on ${cascade_dir} (incremental sampling)"
    python3 generate_queries.py \
	    -g ${graph} \
	    -f ${graph_suffix} \
	    --root_sampler ${root_sampler} \
	    --weighted \
	    --incremental_cascade \
	    -q ${query_method} \
	    -n ${n_queries} \
	    -s 250 \
	    -p ${min_proba} \
	    -m ${sample_method} \
	    -c ${cascade_dir} \
	    -d outputs/queries-weighted/${dataset_id}/${sample_method}/${query_method}-inc
done


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
