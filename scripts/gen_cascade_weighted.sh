#! /bin/zsh

graph="grqc"
graph_suffix='_s0.03'
cascade_model="ic"
n_cascades=96
obs_fraction=0.1
cascade_fraction=0.005
min_size=10
max_size=30


dataset_id="${graph}-m${cascade_model}-s${cascade_fraction}-o${obs_fraction}"

ourput_dir="cascade-weighted/${dataset_id}"

print "output_dir: ${ourput_dir}"

python3 simulate_cascades.py \
	-g ${graph} \
	-f ${graph_suffix} \
	-n ${n_cascades} \
	-o ${obs_fraction} \
	--use_edge_weights \
	-m ${cascade_model} \
	-d ${ourput_dir} \
	-s ${cascade_fraction} \
	--min_size ${min_size} \
	--max_size ${max_size}

