#! /bin/zsh

graphs=(karate lattice dolphin)

for g in ${graphs};do
    # print "python3 generate_queries.py -g $g"
    print "python3 infer_from_queries.py -g $g"
done
