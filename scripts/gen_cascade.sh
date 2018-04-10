#! /bin/zsh

graph="lattice-1024"
n_cascades=12
n_observation_rounds=8
cascade_model="si"
graph_suffix="_0.5"

obs_fraction=0.2
cascade_fraction=0.5

dataset_id="${graph}-m${cascade_model}-s${cascade_fraction}-o${obs_fraction}"

ourput_dir="cascade-weighted/${dataset_id}"

print "ouput to ${ourput_dir}"

python3 simulate_cascades.py \
	-g ${graph} \
	-n ${n_cascades} \
	-o ${obs_fraction} \
	-f ${graph_suffix} \
	--n_observation_rounds ${n_observation_rounds} \
	--use_edge_weights \
	-m ${cascade_model} \
	-d ${ourput_dir} \
	-s ${cascade_fraction} \
	--observation_method uniform
