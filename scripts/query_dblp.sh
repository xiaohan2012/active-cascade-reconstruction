#! /bin/zsh

python3 generate_queries.py \
   -g dblp \
   -n 1000 \
   -s 1000 \
   -c cascade/dblp-s0.2-o0.1/ \
   -d outputs/queries/dblp-s0.2-o0.1/
