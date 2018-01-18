#! /bin/zsh
sample_methods=(loop_erased)
query_methods=(prediction_error)

for query_method in ${query_methods}; do
    for sample_method in ${sample_methods}; do
	python3 generate_queries.py \
		-g grqc \
		-q ${query_method} \
		-n 100 \
		-s 250 \
		-m ${sample_method} \
		-c cascade/grqc/ \
		-d outputs/queries/grqc/${sample_method}/${query_method}-max
    done
done
