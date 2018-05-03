#! /bin/bash

name=flixster
python3 make_stochastic_graph.py ${name}

new_dir=data/${name}-sto
old_dir=data/${name}

if [ ! -d ${new_dir} ]; then
    mkdir ${new_dir}
fi

cp ${old_dir}/graph.gt ${new_dir}/graph.gt
mv ${old_dir}/graph_sto.gt ${new_dir}/graph_weighted.gt
mv ${old_dir}/graph_sto_rev.gt ${new_dir}/graph_weighted_rev.gt
