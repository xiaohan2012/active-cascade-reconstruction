#! /bin/zsh
graph='grqc'
sample_method=loop_erased
query_methods=(random pagerank entropy prediction_error)

cascade_model="ic"
obs_fraction=0.1
min_proba=0.00

dataset_id="${graph}-m${cascade_model}-o${obs_fraction}"

cascade_dir="cascade-weighted/${dataset_id}"


# with weights
for query_method in ${query_methods}; do
    print "${query_method} on ${cascade_dir}"
    python3 generate_queries.py \
	    -g ${graph} \
	    --weighted \
	    -q ${query_method} \
	    -n 100 \
	    -s 250 \
	    -p ${min_proba} \
	    -m ${sample_method} \
	    -c ${cascade_dir} \
	    -d outputs/queries-weighted/${dataset_id}/${sample_method}/${query_method}
done


# without weights
query_methods=(entropy prediction_error)
for query_method in ${query_methods}; do
    print "${query_method} on ${cascade_dir}"
    python3 generate_queries.py \
	    -g ${graph} \
	    -q ${query_method} \
	    -n 100 \
	    -s 250 \
	    -p ${min_proba} \
	    -m ${sample_method} \
	    -c ${cascade_dir} \
	    -d outputs/queries-weighted/${dataset_id}/${sample_method}/${query_method}-unweighted
done