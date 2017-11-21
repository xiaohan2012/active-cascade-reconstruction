#! /bin/zsh

kernprof -l generate_queries.py \
   -g grqc \
   -n 1 \
   -s 100 \
   -c cascade/grqc-s0.2-o0.1/ \
   -d outputs/queries/grqc-s0.2-o0.1/ \
   --debug
