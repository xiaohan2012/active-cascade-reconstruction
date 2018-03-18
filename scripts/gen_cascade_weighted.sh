#! /bin/zsh

graph="lattice-1024"
graph_suffix='_s0.02'
cascade_model="ic"
n_cascades=96
obs_fraction=0.5
stop_fraction=0.03
min_size=10


dataset_id="${graph}-m${cascade_model}-s${stop_fraction}-o${obs_fraction}"

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
	-s ${stop_fraction} \
	--min_size ${min_size}

