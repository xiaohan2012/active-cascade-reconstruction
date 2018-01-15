#! /bin/zsh
query_methods=('random' 'pagerank' 'entropy' 'prediction_error')
sample_method=loop_erased
cascade_ids=({0..9})

for cid in ${cascade_ids}; do
    for query_method in ${query_methods}; do
 	python3 generate_queries.py \
		-g digg \
		-q ${query_method}  \
		-n 100 \
		-s 100 \
		-m ${sample_method} \
		-c cascade/digg/${cid} \
		-d outputs/queries/digg/${cid}/${query_method}
# 	print 	"python3 generate_queries.py \
# -g digg \
# -q ${query_method}  \
# -n 100 \
# -s 500 \
# -m ${sample_method} \
# -c cascade/digg/${cid} \
# -d outputs/queries/digg/${cid}/${query_method}"	
    done
done
