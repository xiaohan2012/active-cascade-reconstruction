# sampling-steiner-tree

# main python scripts

- `make_graph_weighted.py`: dump  graph with edge weights
- `simulate_cascades.py`: simulate cascades and dump to files
- `generate_queries.py`: produce queries and dump to files
- `infer_from_queries.py`: infer the infection probabilities from queries
- `average_precision_score.ipynb`: evaluation using average precision score (should be better than precision and recall)


# shell scripts

## cascade generation

- `gen_cascades_with_varying_size.sh`
- `gen_cascades_with_varying_obs_fraction.sh`

**UPDATE Mar 8**

for IC, cascade size depends on the edge probability. so setting cascade size needs to be done by trying different edge probabilities

to achieve so, do the following

1. generate the weighted graph using `make_weighted_graph.py`
2. generate cascade using `./scripts/gen_cascade_weighted.sh`
3. check the cascade size using `print_cascade_sizes.py`
4. modify the edge weights and go back to 1
5. once you are fine with the size, edit and run `./scripts/mv_graph_and_cascade.sh`

## query

- `query_cascades_with_varying_size.sh`
- `query_cascades_with_varying_obs_fraction.sh`
- `query_weighted_graph.sh`: on weighted graph

note on the directories:

- `outputs/queries-weighted`: for the weighted graph
  - it contain queries using unweighted sampling, then the subdirectory has name `{entropy, prediction_error}-unweighted`
- `outputs/queries`: for the unweighted graph

## inference

- `infer_weighted_cascade.sh`: on weighted graph
- `infer_cascades_with_varying_size.sh`: TBD
- `infer_cascades_with_varying_obs_fraction.sh`: TBD

note on the directories:

- `outputs/inf_probas-weighted`: inference using weighted sampling
- `outputs/inf_probas-unweighted`: inference using unweighted sampling


# misc

- `scripts/query_{dataset}.sh`: generate queries for `${dataset}`
- `scripts/infer_{dataset}.sh`: make inference on infections for `${dataset}`
- `compare_running_time.py`: script to compare running time for different query methods
- `print_cascade_sizes.py`: print simulated cascade statistics

