#! /bin/zsh

graph="grqc"
sample_method=loop_erased
query_method=prediction_error

cascade_model="si"
stop_fraction=0.16
obs_fraction=0.1

dataset_id="${graph}-m${cascade_model}-s${stop_fraction}-o${obs_fraction}"
cascade_dir="cascade/${dataset_id}"

min_probas=(0.05 0.1 0.15 0.20 0.25)
for min_proba in ${min_probas}; do
    query_method_id="${query_method}-p${min_proba}"
    print "${query_method_id} on ${dataset_id}"
    python3 generate_queries.py \
	    -g ${graph} \
	    -q ${query_method} \
	    -p ${min_proba} \
	    -n 100 \
	    -s 250 \
	    -m ${sample_method} \
	    -c ${cascade_dir} \
	    -d outputs/queries/${dataset_id}/${sample_method}/${query_method_id}
done
