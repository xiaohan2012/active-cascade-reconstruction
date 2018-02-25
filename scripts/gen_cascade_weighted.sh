#! /bin/zsh

graph="grqc"
n_cascades=96
obs_fraction=0.1
stop_fraction=0.1
cascade_model="ic"
ourput_dir="cascade-weighted/${graph}-m${cascade_model}-o${obs_fraction}"

python3 simulate_cascades.py \
	-g ${graph} \
	-n ${n_cascades} \
	-o ${obs_fraction} \
	-r \
	-m ${cascade_model} \
	-d ${ourput_dir} \
	-s ${stop_fraction} \
	--min_size 100

