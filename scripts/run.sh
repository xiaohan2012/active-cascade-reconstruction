#! /bin/zsh
# "fb" 
graphs=("lattice-100")
# "lattice-sto";
#
# "flixster-sto"
# "infectious-sto"
# graphs=("grqc-sto")
# "p2p-sto"
graph_suffix=" "

cascade_model="si"
cascade_fraction=0.25
obs_fraction=0.25
obs_methods=("uniform")

n_tree_samples=100  # 2500
sample_method="simulation"

root_sampler='true_root'

# query_methods=(random pagerank entropy prediction_error mutual-info oracle-e oracle-l)
# query_methods=(weighted-cond-ent)
# query_methods=(oracle-e oracle-l)
# query_methods=(prediction_error mutual-info entropy)
query_methods=(entropy random)
# pagerank  cond-entropy 
n_queries=100  # 500
eval_every_k=5
# 0.2 0.3 0.4 0.5
# obs_fractions=(0.1)

min_proba=0.05

n_jobs=-1

for graph in ${graphs}; do
    for obs_method in ${obs_methods}; do
	dataset_id="${graph}-m${cascade_model}-s${cascade_fraction}-o${obs_fraction}-omuniform"
	print "dataset_id: ${dataset_id}"

	cascade_dir="cascade-weighted/${dataset_id}"
	for query_method in ${query_methods}; do
	    print "${query_method} on ${cascade_dir}"
	        python3 generate_queries.py \
	    	    -g ${graph} \
	    	    -f "${graph_suffix}" \
	    	    --root_sampler ${root_sampler} \
	    	    --weighted \
	    	    -q ${query_method} \
	    	    -n ${n_queries} \
	    	    -s ${n_tree_samples} \
	    	    -p ${min_proba} \
	    	    -m ${sample_method} \
	    	    -c ${cascade_dir} \
	    	    -d outputs/queries-weighted/${dataset_id}/${sample_method}/${query_method}  \
	    	    -j ${n_jobs} --verbose
	    

	    python3 infer_from_queries.py \
	    	    -g ${graph} \
	    	    -f "${graph_suffix}" \
	    	    --weighted \
	    	    -s ${n_tree_samples} \
	    	    --sampling_method ${sample_method} \
	    	    -c ${cascade_dir} \
	    	    --query_method ${query_method} \
	    	    --root_sampler ${root_sampler} \
	    	    -q outputs/queries-weighted/${dataset_id}/${sample_method}/${query_method} \
	    	    -p outputs/inf-probas-weighted/${dataset_id}/${sample_method}/${query_method} \
	    	    --eval_every ${eval_every_k} \
	    	    -j ${n_jobs} \
		    --verbose
	done
    done
done
