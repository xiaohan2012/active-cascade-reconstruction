#! /bin/zsh

graph_sizes=(4 5 6 7 8)
sample_sizes=(100000 1000000 10000000)
num_terminals=2

for sample_size in ${sample_sizes}; do
    for graph_size in ${graph_sizes}; do
	output_path="outputs/tree-distribution-experiment-n${graph_size}-x${num_terminals}-k${sample_size}.pkl"
	if [[ ! -a ${output_path} ]]; then
	    python3 tree_distribution_experiment.py \
		    -n ${graph_size} \
		    -x ${num_terminals} \
		    -k ${sample_size} \
		    -o ${output_path}
	else
	    print "${output_path} processed"
	fi
    done
done
