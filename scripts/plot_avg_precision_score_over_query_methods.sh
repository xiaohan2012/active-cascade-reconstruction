#! /bin/zsh

graph="lattice-1024"
sample_method=loop_erased

inf_method="inf_probas"

cascade_model="si"
# stop_fractions=(0.01 0.02 0.04 0.08 0.16 0.32)
stop_fractions=(0.04 0.08 0.16 0.32 0.64)
obs_fraction=0.1
query_methods="random, pagerank, entropy, prediction_error"

for stop_fraction in ${stop_fractions}; do
    data_id="${graph}-m${cascade_model}-s${stop_fraction}-o${obs_fraction}"
    # print "${data_id}"

    if (( ${stop_fraction} == 0.01 )); then
	n_queries=20
    elif (( ${stop_fraction} == 0.02 )); then
	n_queries=40
    elif (( ${stop_fraction} == 0.04 )); then
	n_queries=40
    else
	n_queries=100
    fi
    print "
    python3 plot_average_precision_score.py \
	    -g ${graph} \
	    -c ${data_id} \
	    -s ${sample_method} \
	    -i ${inf_method} \
	    -n ${n_queries} \
            -q '${query_methods}' \
            -f ${data_id}
"
done
