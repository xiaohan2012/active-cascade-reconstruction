#! /bin/zsh

graph="grqc"
sample_method=cut
query_methods=(random pagerank entropy prediction_error)

cascade_model="ic"
obs_fraction=0.5
stop_fraction=0.03
min_proba=0.00
graph_suffix="_s${stop_fraction}"

root_sampler='random'

dataset_id="${graph}-m${cascade_model}-s${stop_fraction}-o${obs_fraction}"

cascade_dir="cascade-weighted/${dataset_id}"

print "dataset_id: ${dataset_id}"

# with weights
for query_method in ${query_methods}; do
    print "${query_method} on ${cascade_dir}"
    python3 generate_queries.py \
	    -g ${graph} \
	    -f ${graph_suffix} \
	    --root_sampler ${root_sampler} \
	    --weighted \
	    -q ${query_method} \
	    -n 100 \
	    -s 250 \
	    -p ${min_proba} \
	    -m ${sample_method} \
	    -c ${cascade_dir} \
	    -d outputs/queries-weighted/${dataset_id}/${sample_method}/${query_method}
done
