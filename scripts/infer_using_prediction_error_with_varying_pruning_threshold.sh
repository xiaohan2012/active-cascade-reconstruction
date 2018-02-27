#! /bin/zsh

graph="grqc"
sample_method=loop_erased
query_method=prediction_error
inf_method="inf_probas"

cascade_model="si"
stop_fraction=0.16
obs_fraction=0.1

dataset_id="${graph}-m${cascade_model}-s${stop_fraction}-o${obs_fraction}"
cascade_dir="cascade/${dataset_id}"

min_probas=(0.05 0.1 0.15 0.20 0.25)
for min_proba in ${min_probas}; do
    query_method_id="${query_method}-p${min_proba}"
    print "infer ${query_method_id} on ${dataset_id}"
    python3 infer_from_queries.py \
	    -g ${graph} \
	    -s 250 \
	    -m ${inf_method} \
	    -c ${cascade_dir} \
	    --query_method ${query_method_id} \
	    -q outputs/queries/${dataset_id}/${sample_method}/${query_method_id} \
	    -p outputs/${inf_method}/${dataset_id}/${sample_method}/${query_method_id}
done
