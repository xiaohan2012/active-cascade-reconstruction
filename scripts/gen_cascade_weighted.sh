#! /bin/zsh

graph="lattice-1024-sto"
cascade_model="si"
n_cascades=12
n_observation_rounds=8
cascade_fraction=0.25
obs_fraction=0.2
min_size=20
max_size=9999999


dataset_id="${graph}-m${cascade_model}-s${cascade_fraction}-o${obs_fraction}"

ourput_dir="cascade-weighted/${dataset_id}"

print "output_dir: ${ourput_dir}"

python3 simulate_cascades.py \
	-g ${graph} \
	-n ${n_cascades} \
	-o ${obs_fraction} \
	--n_observation_rounds ${n_observation_rounds} \
	--use_edge_weights \
	-m ${cascade_model} \
	-d ${ourput_dir} \
	-s ${cascade_fraction} \
	--min_size ${min_size} \
	--max_size ${max_size} \
	--observation_method uniform
