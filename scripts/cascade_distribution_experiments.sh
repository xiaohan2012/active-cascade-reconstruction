#! /bin/zsh

# graph_sizes=(4 5 6 7 8)
# sample_sizes=(100000 1000000 10000000)
graph_sizes=(8)
sample_sizes=(1000000)
num_terminals=(2 3 4 5 6 7)

for num_terminal in ${num_terminals}; do
    for sample_size in ${sample_sizes}; do
	for graph_size in ${graph_sizes}; do
	    output_path="outputs/cascade-distribution-experiment-n${graph_size}-x${num_terminal}-k${sample_size}.pkl"
	    if [[ ! -a ${output_path} ]]; then
		python3 cascade_distribution_experiment.py \
			-n ${graph_size} \
			-x ${num_terminal} \
			-k ${sample_size} \
			-o ${output_path}
	    else
		print "${output_path} processed"
	    fi
	done
    done
done
