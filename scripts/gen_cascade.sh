#! /bin/zsh

graph="email-univ"

n_cascades=96
cascade_model="ic"
graph_suffix="_0.5"

root_dir="/experiment/cascades/"
obs_method="uniform"
obs_fraction=0.1

min_fraction=0.025
max_fraction=0.025

ROOT_DIR=/experiment/cascades

dataset_id="${graph}-m${cascade_model}-s${max_fraction}-o${obs_fraction}-om${obs_method}"
output_dir="${root_dir}/${dataset_id}"

echo "output to ${output_dir}"

python3 simulate_cascades.py \
	-g ${graph} \
	-n ${n_cascades} \
	-o ${obs_fraction} \
	-f ${graph_suffix} \
	-m ${cascade_model} \
	-d ${output_dir} \
	--observation_method ${obs_method} \
	--use_edge_weights \
	--min_fraction ${min_fraction} \
	--max_fraction ${max_fraction}
