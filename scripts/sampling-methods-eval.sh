#! /bin/zsh

graphs=('lattice-1024' 'grqc' 'fb')
graph_suffices=("0.02" '0.03' '0.2')

obs_fractions=(0.1 0.25 0.5 0.75)


for i ({1..3}); do
    # print ${i}
    graph=${graphs[${i}]}
    graph_suffix=${graph_suffices[${i}]}
    
    for obs_fraction in ${obs_fractions}; do
	output_path="outputs/inf_probas/${graph}-s${graph_suffix}-q${obs_fraction}.pkl"
	# print ${output_path}
	print "python3 sampling_methods_evaluation.py \
-g ${graph} \
-f s${graph_suffix} \
-q ${obs_fraction}"
    done
done
