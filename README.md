# sampling-steiner-tree

# get started

We made a Docker image that provides the running environment, you can pull from the Docker:

```
> docker pull xiaohan2012/active_cascade_reconstruction
```

Then, you can enter the container's shell environment:

```
> cd active_cascade_reconstruction
> ./start_docker.sh
# (now, you are in docker container)
```

To test the code,

```
> cd /code/active_cascade_reconstruction
> pytest test*.py
```

# algorithm files

- query selection algorithms
  - `query_selection.py`: random, pagerank, entropy, prediction\_error
  - `tree_stat.py`: query score calculation for entropy and prediction\_error,
  - `sample_pool.py`: steiner tree sampling part (including incrementally sample update upon queries)
- estimating infection probability
  - `inference.py`: also calls functions in `tree_stat.py`

# main experiment scripts

- `make_graph_weighted.py`: dump  graph with edge weights
- `simulate_cascades.py`: simulate cascades and dump to files
- `generate_queries.py`: [batch] produce queries and dump to files
  - `query_one_round.py`: [single] produce queries and dump to file
- `infer_from_queries.py`: [in batch] infer the infection probabilities from queries
  - `infer_one_round.py`: [single]
- `query_process_illustration.py`: visualize different query strategies

## typical pipeline to run experiment

1. `./scripts/gen_cascade.sh`: generate the cascades
2. `./scripts/run.sh`: generate queries and infer the infection proability
3. `./scripts/eval_plot.sh`: performance evaluation and plotting

## pipeline on Triton

1. edit the configuration file under `exp_configs/`
2. `python3 runner.py --name {name_of_the_config_file_editted_before}`
   - the sbatch file path will be printed as `${path_of_sbatch_file}`
3. `sbatch ${path_of_sbatch_file}` to submit the job
   - the result will be saved to postgres DB
4. optionally, you can view the result in the database

## plotting scripts

- `sample_size_effect_plot.py`: inference performance by effect of sample size using different sampling methods
- `compare_query_methods_plot.py`: comparing different query strategies

## note on Triton

use `./singularity/exec.sh ${cmd_to_exec}` to execute the command in the singularity container

---------------------

possibly deprecated

# shell scripts

## graph preprocessing

- use `make_graph_weighted.py` to add weights and use the resulting graph to simulate cascade
- use `preprocess_graph.py` to apply global normalization and edge reversing

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

- `run.sh`: run the query selection as well as inference part
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
