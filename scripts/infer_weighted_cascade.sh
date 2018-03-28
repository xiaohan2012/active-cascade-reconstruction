#! /bin/zsh

graph="grqc"
graph_suffix="_preprocessed"
obs_fraction="leaves"
cascade_fraction=0.02

sample_method=cut
cascade_model="ic"
root_sampler='true_root'
query_methods=(random pagerank entropy prediction_error)

inf_method="inf_probas"




dataset_id="${graph}-m${cascade_model}-s${cascade_fraction}-o${obs_fraction}"

cascade_dir="cascade-weighted/${dataset_id}"
print "on ${dataset_id}"
for query_method in ${query_methods}; do
    # infer on weighted graph using weighted queries 
    python3 infer_from_queries.py \
	    -g ${graph} \
	    -f ${graph_suffix} \
	    --weighted \
	    -s 250 \
	    -m ${inf_method} \
	    -c ${cascade_dir} \
	    --query_method ${query_method} \
	    --root_sampler ${root_sampler} \
	    -q outputs/queries-weighted/${dataset_id}/${sample_method}/${query_method} \
	    -p outputs/${inf_method}-weighted/${dataset_id}/${sample_method}/${query_method}
	    # --with_inc_sampling

    # # infer on unweighted graph using weighted queries
    # # this is done to check the effects of edge weights on inference performance
    # python3 infer_from_queries.py \
    # 	    -g ${graph} \
    # 	    -f ${graph_suffix} \	    
    # 	    -s 250 \
    # 	    -m ${inf_method} \
    # 	    -c ${cascade_dir} \
    # 	    --query_method ${query_method} \
    # 	    -q outputs/queries-weighted/${dataset_id}/${sample_method}/${query_method} \
    # 	    -p outputs/${inf_method}-unweighted/${dataset_id}/${sample_method}/${query_method}
done


# query_methods=(entropy prediction_error)

# for query_method in ${query_methods}; do
#     # infer on weighted graph using unweighted queries
#     python3 infer_from_queries.py \
# 	    -g ${graph} \
# 	    --weighted \
# 	    -s 250 \
# 	    -m ${inf_method} \
# 	    -c ${cascade_dir} \
# 	    --query_method ${query_method} \
# 	    -q outputs/queries-weighted/${dataset_id}/${sample_method}/${query_method}-unweighted \
# 	    -p outputs/${inf_method}-weighted/${dataset_id}/${sample_method}/${query_method}-unweighted
# done
