#! /bin/zsh

graph="lattice-1024"
sample_method=loop_erased

inf_method="inf_probas"

cascade_model="si"
# stop_fractions=(0.02 0.04 0.08 0.16 0.32)
stop_fractions=(0.04 0.08 0.16 0.32 0.64)
obs_fraction=0.1

query_methods=(random pagerank entropy prediction_error)

for stop_fraction in ${stop_fractions}; do
    dataset_id="${graph}-m${cascade_model}-s${stop_fraction}-o${obs_fraction}"

    cascade_dir="cascade/${dataset_id}"
    print "on ${dataset_id}"
    for query_method in ${query_methods}; do
	python3 infer_from_queries.py \
		-g ${graph} \
		-s 250 \
		-m ${inf_method} \
		-c ${cascade_dir} \
		--query_method ${query_method} \
		-q outputs/queries/${dataset_id}/${sample_method} \
		-p outputs/${inf_method}/${dataset_id}/${sample_method}
	
    done
done
