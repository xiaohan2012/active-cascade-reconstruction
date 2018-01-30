#! /bin/zsh

# for si model, you can control the cascade size by stop_fraction
# for ic odel, you can control the cascade size by infection probability

# change this!!
graph="p2p"

n_cascades=96
stop_fractions=(0.01 0.02 0.04 0.08 0.16 0.32)
obs_fraction=0.1
cascade_model="si"
infection_proba=0.5


for stop_fraction in ${stop_fractions}; do
    print "stop_fraction=${stop_fraction}"
    ourput_dir="cascade/${graph}-m${cascade_model}-s${stop_fraction}-o${obs_fraction}"
    python3 simulate_cascades.py \
	    -g ${graph} \
	    -n ${n_cascades} \
	    -o ${obs_fraction} \
	    -p ${infection_proba} \
	    -s ${stop_fraction} \
	    -m ${cascade_model} \
	    -d ${ourput_dir} 
done

