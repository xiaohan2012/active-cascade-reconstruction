#! /bin/zsh

graph_sizes=(4 5 6 7 8)
sample_sizes=(100000 1000000 10000000)
num_terminals=2

for sample_size in ${sample_sizes}; do
    for graph_size in ${graph_sizes}; do
	python3 cascade_distribution_experiment.py \
		-n ${graph_size} \
		-x ${num_terminals} \
		-k ${sample_size} \
		-o  "outputs/cascade-distribution-experiment-n${graph_size}-x${num_terminals}-k${sample_size}.pkl"
    done
done
