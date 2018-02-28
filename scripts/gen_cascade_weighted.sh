#! /bin/zsh

graph="grqc"
cascade_model="si"
n_cascades=96
obs_fraction=0.1
stop_fraction=0.08


if [ ${cascade_model} == "ic" ]; then    
    dataset_id="${graph}-m${cascade_model}-o${obs_fraction}"
else
    dataset_id="${graph}-m${cascade_model}-s${stop_fraction}-o${obs_fraction}"
fi

ourput_dir="cascade-weighted/${dataset_id}"

python3 simulate_cascades.py \
	-g ${graph} \
	-n ${n_cascades} \
	-o ${obs_fraction} \
	-r \
	-m ${cascade_model} \
	-d ${ourput_dir} \
	-s ${stop_fraction} \
	--min_size 100

