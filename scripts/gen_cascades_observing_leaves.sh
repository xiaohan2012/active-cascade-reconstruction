#! /bin/zsh

graph="p2p"
cascade_model="ic"
n_cascades=96
cascade_fraction=0.02
obs_fraction=0.5
min_size=80
max_size=160
obs_method="leaves"

dataset_id="${graph}-m${cascade_model}-s${cascade_fraction}-o${obs_method}"

ourput_dir="cascade-weighted/${dataset_id}"

print "output_dir: ${ourput_dir}"

python3 simulate_cascades.py \
	-g ${graph} \
	-n ${n_cascades} \
	-o ${obs_fraction} \
	--use_edge_weights \
	-m ${cascade_model} \
	-d ${ourput_dir} \
	-s ${cascade_fraction} \
	--min_size ${min_size} \
	--max_size ${max_size} \
	--observation_method ${obs_method}
