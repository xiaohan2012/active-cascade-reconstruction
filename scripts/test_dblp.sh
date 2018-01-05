#! /bin/zsh

kernprof -l generate_queries.py \
   -g dblp \
   -n 1 \
   -s 100 \
   -c cascade/dblp-s0.2-o0.1/ \
   -d outputs/queries/dblp-s0.2-o0.1/ \
   --debug
