#! /bin/zsh

graph="lattice-1024"
sample_method=loop_erased
query_methods=(entropy)
inf_method="inf_probas"

cascade_model="ic"
obs_fraction=0.1
stop_fraction=0.02
min_proba=0.00
graph_suffix="_s${stop_fraction}"

normalize_p='div_max'

dataset_id="${graph}-m${cascade_model}-s${stop_fraction}-o${obs_fraction}"

cascade_dir="cascade-weighted/${dataset_id}"

print "dataset_id: ${dataset_id}"

# with weights
for query_method in ${query_methods}; do
    print "${query_method} on ${cascade_dir}"
    python3 generate_queries.py \
	    -g ${graph} \
	    -f ${graph_suffix} \
	    --weighted \
	    -q ${query_method} \
	    -n 100 \
	    -s 250 \
	    -p ${min_proba} \
	    -m ${sample_method} \
	    -c ${cascade_dir} \
	    --normalize_proba ${normalize_p} \
	    -d outputs/queries-weighted/${dataset_id}/${sample_method}/${query_method}-with-norm-p

    python3 infer_from_queries.py \
    	    -g ${graph} \
    	    -f ${graph_suffix} \
    	    --weighted \
    	    -s 250 \
    	    -m ${inf_method} \
    	    -c ${cascade_dir} \
    	    --query_method ${query_method} \
    	    -q outputs/queries-weighted/${dataset_id}/${sample_method}/${query_method}-with-norm-p \
    	    -p outputs/${inf_method}-weighted/${dataset_id}/${sample_method}/${query_method}-with-norm-p
done


