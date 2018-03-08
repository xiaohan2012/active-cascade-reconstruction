#! /bin/zsh

graph='grqc'
fraction=0.1

mv data/${graph}/graph_weighted_tmp.gt data/${graph}/graph_weighted_s${fraction}.gt
mv cascade-weighted/${graph}-mic-s0-o0.1 cascade-weighted/${graph}-mic-s${fraction}-o0.1
