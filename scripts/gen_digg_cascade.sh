#! /bin/zsh

ids=({0..9})
graph="digg"
n_cascades=10
obs_fraction=0.1
ourput_dir="cascade/${graph}"
cascasde_path_prefix="data/digg/cascade_"

for id in ${ids}; do
    print "python3 simulate_cascades.py -g ${graph} -n ${n_cascades} -o ${obs_fraction} -d ${ourput_dir}/${id} -c ${cascasde_path_prefix}${id}.pkl"
done
