#! /bin/zsh

graph="grqc-sto"
n_cascades=12
n_observation_rounds=8
# n_cascades=8
# n_observation_rounds=1
cascade_model="ic"
graph_suffix=" "

obs_fraction=0.2
# works for IC
min_size=100
max_size=1000

# works for SI
cascade_fraction=0.01

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
	--observation_method uniform \
	--min_size ${min_size} \
	--max_size ${max_size}
