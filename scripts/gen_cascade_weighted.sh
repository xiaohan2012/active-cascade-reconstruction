#! /bin/zsh

graph="grqc"
graph_suffix='_tmp'
cascade_model="ic"
n_cascades=96
obs_fraction=0.1
stop_fraction=0
min_size=10


if [ ${cascade_model} = "ic" ]; then    
    dataset_id="${graph}-m${cascade_model}-s${stop_fraction}-o${obs_fraction}"
else
    dataset_id="${graph}-m${cascade_model}-s${stop_fraction}-o${obs_fraction}"
fi

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

