#! /bin/zsh

sampling_methods=("cut" "loop_erased")
# "inf_probas" 
inference_methods=("order_steiner_tree")


for sampling_method in ${sampling_methods}; do
    for inf_method in ${inference_methods}; do
	print "sampling_method=${sampling_method} inf_method=${inf_method}"
	python3 infer_from_queries.py \
		-g grqc \
		-s 250 \
		-m ${inf_method} \
		-c cascade/grqc/ \
		-q outputs/queries/grqc/${sampling_method} \
		-p outputs/${inf_method}/grqc/${sampling_method}
    done
done
