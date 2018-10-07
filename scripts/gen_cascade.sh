#! /bin/zsh

graph="lattice-100"

n_cascades=96
n_observation_rounds=1
# n_cascades=8
# n_observation_rounds=1
cascade_model="si"
graph_suffix="_0.5"

obs_method="uniform"
obs_fraction=0.1

# works for IC
min_size=100
max_size=1000

ROOT_DIR=/experiment/cascades

# works for SI
cascade_fraction=0.1
dataset_id="${graph}-m${cascade_model}-s${cascade_fraction}-o${obs_fraction}-om${obs_method}"

# copy from existing cascades
output_dir="${ROOT_DIR}/${dataset_id}"
from_cascade_dir="${ROOT_DIR}/${graph}-m${cascade_model}-s${cascade_fraction}-o${obs_fraction}-ombfs-head"

echo "output to ${output_dir}"

python3 simulate_cascades.py \
	-g ${graph} \
	-n ${n_cascades} \
	-o ${obs_fraction} \
	-f ${graph_suffix} \
	--n_observation_rounds ${n_observation_rounds} \
	-m ${cascade_model} \
	-d ${output_dir} \
	-s ${cascade_fraction} \
	--observation_method ${obs_method} \
	--use_edge_weights \
	--min_size ${min_size} \
	--max_size ${max_size}
	# -c ${from_cascade_dir}
