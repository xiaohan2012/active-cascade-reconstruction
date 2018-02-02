#! /bin/zsh

graph="p2p"
sample_method=loop_erased
query_methods=(random pagerank entropy prediction_error)

cascade_model="si"
stop_fractions=(0.02 0.04 0.08 0.16 0.32)
# stop_fractions=(0.04 0.08 0.16 0.32 0.64)
obs_fraction=0.1
min_proba=0.05

for stop_fraction in ${stop_fractions}; do
    dataset_id="${graph}-m${cascade_model}-s${stop_fraction}-o${obs_fraction}"

    cascade_dir="cascade/${dataset_id}"
    for query_method in ${query_methods}; do
	print "${query_method} on ${dataset_id}"
	python3 generate_queries.py \
		-g ${graph} \
		-q ${query_method} \
		-n 100 \
		-s 250 \
		-p ${min_proba} \
		-m ${sample_method} \
		-c ${cascade_dir} \
		-d outputs/queries/${dataset_id}/${sample_method}/${query_method}
    done
done
