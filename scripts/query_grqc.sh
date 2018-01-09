#! /bin/zsh
methods=(cut loop_erased)


for method in ${methods}; do
    python3 generate_queries.py \
	    -g grqc \
	    -q prediction_error \
	    -n 100 \
	    -s 100 \
	    -m ${method} \
	    -c cascade/grqc-s0.2-o0.1/ \
	    -d outputs/queries/grqc-s0.2-o0.1/${method}/
done
