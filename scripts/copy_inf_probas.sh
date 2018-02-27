#! /bin/zsh
# copy inf probas from weighted to unweighted directory
# for the ease of plotting

data_id="grqc-mic-o0.1"
methods=(random pagerank prediction_error entropy)
ROOT=/home/cloud-user/code/active-network-reconstruction

for method in ${methods}; do
    target="${ROOT}/outputs/inf_probas-unweighted/${data_id}/loop_erased/${method}-weighted"
    if [ ! -L ${target} ]; then
	ln -s \
	   ${ROOT}/outputs/inf_probas-weighted/${data_id}/loop_erased/${method} \
	   ${target}
    else
	print "${target} exists"
    fi
done
