#! /bin/zsh

graphs=('lattice-1024' 'grqc' 'fb')
graph_suffix="_preprocessed"

# 1% to 2% infections
min_sizes=(20 40 40)
max_sizes=(40 80 80)

n_runs=$((8 * 96))
obs_fractions=(0.1 0.25 0.5 0.75)


for i ({1..3}); do
    print ${i}
    graph=${graphs[${i}]}
    min_size=${min_sizes[${i}]}
    max_size=${max_sizes[${i}]}
    
    for obs_fraction in ${obs_fractions}; do
	output_path="outputs/inf_probas/${graph}-s${min_size}-${max_size}-q${obs_fraction}.pkl"
	print ${output_path}
	python3 sampling_methods_experiment.py \
		-g ${graph} \
		-f ${graph_suffix} \
		--min_size ${min_size} \
		--max_size ${max_size} \
		-n ${n_runs} \
		-q ${obs_fraction} \
		-o ${output_path}
    done
done
