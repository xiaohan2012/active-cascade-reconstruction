
# query/infer weighted graph

0. [X] generate the weighted graph
1. [X] generate IC cascade using random edge weight for different graphs
   - uniform random from `[0.001, 0.25]` (for grqc)
   - avg cascade size: 330 (for grqc)
2. [X] for query algorithms: entropy and prediction-error, make sure the sampling methods consider the edge weight
   - also run the sampling based algorithm on unweighted graph as baselines
3. inference algorithm consider the edge weight
   - weighted and unweighted version

# evaluation criteria impact

- option 1: include infected queries in the test set
- option 2: exclude all queries in the test set

observation:

- for option 1, ranking is entropy > pagerank > prederror > random
- entropy and pagerank are good at query infected nodes 
- inference algorithm tends to low infection probability to all nodes (even for infected nodes)
  - therefore for entropy, if infection probability is close to 0.5, it's very likely to be infected, therefore highly infected nodes are the most uncertain nodes (no way!)
  - also, for prederror, which internally uses entropy, is infected by this as well.

to think:

- the validity of the inference algorithm
- choice on evaluation criteria

# normlizing the infection probability

by `p /= p.max()`

both entropy and prederror gives better result than itself before.

- for lattice: http://193.166.24.212/active-network-reconstruction/figs/average_precision_score/lattice-1024-mic-s0.02-o0.1.pdf
- for grqc: http://193.166.24.212/active-network-reconstruction/figs/average_precision_score/grqc-mic-s0.03-o0.1.pdf

things to check:

- do we need importance resampling?
- any bug in the code?

# TODO

- [X] query/infer weighted SI model on grqc
- [X] query illustration of lattice graph
- weighted version on lattice graph
  - [ ] SI, does not give results to all cascades
  - [X] IC

- [ ] plot effects of cascade model
- [ ] why fb is so good

# probabilistic trimming and cross entropy evaluation

- [X] probabilistic trimming
- [ ] possible methods
  - {personalized pagerank root, random root} x deterministic/probabilistic trimming
- [X] personalzied pagerank with noise
- [ ] cross entropy measure for evaluation
- [ ] compare which inference algorithm (inc or not) gives better result?
  - it might be because of the incorrectness of inference method, the final result becomes bad (however, prederror's queries are still good)
- [ ] check bug

## sampling algorithm on inference result

## note on evaluation metrics

- auc: very close to 1, because of the large fraction of uninfected nodes
- precision/recall/f1: much lower (around 0.5)
- ap score: similar to f1

## note on baseline inference method random

it gives:

- close to zero ap, precision, and f1.
- close to 0.5 auc and recall

so our inference algorithm makes sense

## effect of `q`

## effect of root sampling

random is actually better than pagerank, but worse than `true root`

##  effect of sampling algorithm

it depends on `q` and evaluation metric.

in general, `incremental` achieves larger recall but lower precision and lower overall f1


## on final evaluation

we need to produce the inferred probability as accurate as possible, 
however for now, it's not very possible.
what we can do:

- use IC cascade samples
- use the actual source (it plays a huge difference)



