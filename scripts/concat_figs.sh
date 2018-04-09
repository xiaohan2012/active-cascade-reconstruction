#! /bin/zsh

graphs=("lattice-1024" "grqc")

cascade_models=("ic" "si")
cascade_frac="0.02"

eval_methods=("precision_at_cascade_size" "ap")

obs_fraction="0.*"

for graph in ${graphs}; do
    for cascade_model in ${cascade_models}; do
	for eval_method in ${eval_methods}; do
	    convert +append \
		    figs/${eval_method}/${graph}-m${cascade_model}-s${cascade_frac}-o${obs_fraction}.pdf \
		    figs/${eval_method}/${graph}-m${cascade_model}-s${cascade_frac}-o.pdf
	done
    done
done
