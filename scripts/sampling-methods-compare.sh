#! /bin/zsh

graphs=('lattice-1024' 'grqc' 'p2p')
graph_suffix="_preprocessed"

# 1% to 2% infections
min_sizes=(40 40 80)
max_sizes=(80 120 160)

n_runs=$((1 * 96))
obs_fractions=("0.1")
observation_method="leaves"


for i ({1..3}); do
    print ${i}
    graph=${graphs[${i}]}
    min_size=${min_sizes[${i}]}
    max_size=${max_sizes[${i}]}
    
    for obs_fraction in ${obs_fractions}; do
	# output_path="outputs/inf_probas/${graph}-s${min_size}-${max_size}-q${obs_fraction}.pkl"
	output_path="outputs/inf_probas/${graph}-s${min_size}-${max_size}-o${observation_method}.pkl"
	print ${output_path}
	python3 sampling_methods_experiment.py \
		-g ${graph} \
		-f ${graph_suffix} \
		--min_size ${min_size} \
		--max_size ${max_size} \
		-n ${n_runs} \
		-q ${obs_fraction} \
		-o ${output_path} \
		--observation_method ${observation_method}
    done
done
