#! /bin/zsh

graph="astro"
n_cascades=96
obs_fraction=0.1
ourput_dir="cascade/${graph}"

python3 simulate_cascades.py -g ${graph} -n ${n_cascades} -o ${obs_fraction} -p 0.5 -d ${ourput_dir}

