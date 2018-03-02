#! /bin/zsh

graph="grqc"
sample_method=loop_erased
inf_method="inf_probas"

cascade_model="si"
obs_fraction=0.1
stop_fraction=0.08

query_methods=(random pagerank entropy prediction_error)

if [ ${cascade_model} = "ic" ]; then    
    dataset_id="${graph}-m${cascade_model}-o${obs_fraction}"
else
    dataset_id="${graph}-m${cascade_model}-s${stop_fraction}-o${obs_fraction}"
fi

cascade_dir="cascade-weighted/${dataset_id}"
print "on ${dataset_id}"
for query_method in ${query_methods}; do
    # infer on weighted graph using weighted queries 
    python3 infer_from_queries.py \
	    -g ${graph} \
	    --weighted \
	    -s 250 \
	    -m ${inf_method} \
	    -c ${cascade_dir} \
	    --query_method ${query_method} \
	    -q outputs/queries-weighted/${dataset_id}/${sample_method}/${query_method} \
	    -p outputs/${inf_method}-weighted/${dataset_id}/${sample_method}/${query_method}

    # infer on unweighted graph using weighted queries
    # this is done to check the effects of edge weights on inference performance
    python3 infer_from_queries.py \
	    -g ${graph} \
	    -s 250 \
	    -m ${inf_method} \
	    -c ${cascade_dir} \
	    --query_method ${query_method} \
	    -q outputs/queries-weighted/${dataset_id}/${sample_method}/${query_method} \
	    -p outputs/${inf_method}-unweighted/${dataset_id}/${sample_method}/${query_method}
done


query_methods=(entropy prediction_error)

for query_method in ${query_methods}; do
    # infer on weighted graph using unweighted queries
    python3 infer_from_queries.py \
	    -g ${graph} \
	    --weighted \
	    -s 250 \
	    -m ${inf_method} \
	    -c ${cascade_dir} \
	    --query_method ${query_method} \
	    -q outputs/queries-weighted/${dataset_id}/${sample_method}/${query_method}-unweighted \
	    -p outputs/${inf_method}-weighted/${dataset_id}/${sample_method}/${query_method}-unweighted
done
