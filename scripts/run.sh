#! /bin/zsh

CASCADE_ROOT_DIR=/experiment/cascades
QUERIES_ROOT_DIR=/experiment/outputs/queries
INFERENCE_ROOT_DIR=/experiment/outputs/inference

graphs=("infectious" "student" "email-univ")

infection_proba=0.5
graph_suffix="_${infection_proba}"

cascade_model="si"
cascade_fraction=0.1
obs_fraction=0.1
obs_methods=("uniform")


n_tree_samples=100  # 2500
sample_method="simulation"

root_sampler='true_root'

query_methods=(cond-entropy entropy pagerank random)

# this is VERY important for simulated-based sampler
# if it's too big (e.g, > casade size), it's extremely hard to accept the samples
# I would suggest making n_queries slightly  smaller than #hidden infections
# for example, for infectious (|V|=410)+ cascade_size = 0.1 and obs_fraction = 0.1
# #hidden nodes = 36.9
# I would set n_queries=15
n_queries=15
eval_every_k=5

min_proba=0.05

n_jobs=-1

for graph in ${graphs}; do
    for obs_method in ${obs_methods}; do
	dataset_id="${graph}-m${cascade_model}-s${cascade_fraction}-o${obs_fraction}-omuniform"
	print "dataset_id: ${dataset_id}"

	cascade_dir="${CASCADE_ROOT_DIR}/${dataset_id}"
	for query_method in ${query_methods}; do
	    print "${query_method} on ${cascade_dir}"
	        python3 generate_queries.py \
	    	    -g ${graph} \
	    	    -f "${graph_suffix}" \
	    	    --root_sampler ${root_sampler} \
	    	    -q ${query_method} \
	    	    -n ${n_queries} \
	    	    -s ${n_tree_samples} \
	    	    -p ${min_proba} \
	    	    -m ${sample_method} \
	    	    -c ${cascade_dir} \
	    	    -d ${QUERIES_ROOT_DIR}/${dataset_id}/${sample_method}/${query_method}  \
	    	    -j ${n_jobs} --verbose \
		    --infection_proba ${infection_proba} \
		    --cascade_size ${cascade_fraction} \
		    --cascade_model ${cascade_model}
	    

	    python3 infer_from_queries.py \
	    	    -g ${graph} \
	    	    -f "${graph_suffix}" \
	    	    -s ${n_tree_samples} \
	    	    --sampling_method ${sample_method} \
	    	    -c ${cascade_dir} \
	    	    --query_method ${query_method} \
	    	    --root_sampler ${root_sampler} \
	    	    -q ${QUERIES_ROOT_DIR}/${dataset_id}/${sample_method}/${query_method} \
	    	    -p ${INFERENCE_ROOT_DIR}/${dataset_id}/${sample_method}/${query_method} \
	    	    --eval_every ${eval_every_k} \
	    	    -j ${n_jobs} \
		    --verbose \
		    --infection_proba ${infection_proba} \
		    --cascade_size ${cascade_fraction} \
		    --cascade_model ${cascade_model}
	done
    done
done
