#! /bin/zsh

graph="grqc"
sample_method=cut
query_methods=(entropy prediction_error)
inf_method="inf_probas"

cascade_model="ic"
obs_fraction=0.1
cascade_fraction=0.005
min_proba=0.00
graph_suffix="_s0.03"
gn_suffix="_gn"

n_queries=10
root_sampler='random'

dataset_id="${graph}-m${cascade_model}-s${cascade_fraction}-o${obs_fraction}"

cascade_dir="cascade-weighted/${dataset_id}"

print "dataset_id: ${dataset_id}"

# query
for query_method in ${query_methods}; do
    print "${query_method} on ${cascade_dir}"
    python3 generate_queries.py \
	    -g ${graph} \
	    -f "${graph_suffix}${gn_suffix}" \
	    --root_sampler ${root_sampler} \
	    --weighted \
	    -q ${query_method} \
	    -n ${n_queries} \
	    -s 250 \
	    -p ${min_proba} \
	    -m ${sample_method} \
	    -c ${cascade_dir} \
	    -d outputs/queries-weighted/${dataset_id}${gn_suffix}/${sample_method}/${query_method}
done


# inference
for query_method in ${query_methods}; do
    python3 infer_from_queries.py \
	    -g ${graph} \
	    -f "${graph_suffix}${gn_suffix}" \
	    --weighted \
	    -s 250 \
	    -m ${inf_method} \
	    -c ${cascade_dir} \
	    --query_method ${query_method} \
	    --root_sampler ${root_sampler} \
	    -q outputs/queries-weighted/${dataset_id}${gn_suffix}/${sample_method}/${query_method} \
	    -p outputs/${inf_method}-weighted/${dataset_id}${gn_suffix}/${sample_method}/${query_method}
    
done


query_dirname='queries-weighted'
cascade_dirname='cascade-weighted'
inf_dirname='inf_probas-weighted'

eval_method="ap"

query_dir_ids="entropy, prediction_error"
inf_dir_ids="entropy, prediction_error"
labels="entropy, prederror"

python3 plot_average_precision_score.py \
	-g ${graph} \
	-d ${dataset_id}${gn_suffix} \
        -e ${eval_method} \
	-c ${cascade_dirname} \
	--query_dirname ${query_dirname} \
	--inf_dirname ${inf_dirname} \
	-s ${sample_method} \
	-n ${n_queries} \
        --query_dir_ids ${query_dir_ids} \
	--inf_dir_ids ${inf_dir_ids} \
	--legend_labels ${labels} \
        -f ${dataset_id}${gn_suffix}


