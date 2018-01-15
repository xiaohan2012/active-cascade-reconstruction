#! /bin/zsh
sampling_methods=(cut loop_erased)
query_methods=(prediction_error entropy pagerank random )

for sampling in ${sampling_methods}; do
    for query_method in ${query_methods}; do
	python3 generate_queries.py \
		-g astro \
		-q ${query_method} \
		-n 100 \
		-s 200 \
		-m ${sampling} \
		-c cascade/astro/ \
		-d outputs/queries/astro/${sampling}/${query_method}
    done
done
