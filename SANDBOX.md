
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

- for ap: `st_inc` is better when `q<0.5` 
- for roc: `st_inc` is always better


## effect of root sampling

random is actually better than pagerank, but worse than `true root`

## effect of sampling algorithm

it depends on `q` and evaluation metric.

in general, `incremental` achieves larger recall but lower precision and lower overall f1


## on final evaluation

we need to produce the inferred probability as accurate as possible, 
however for now, it's not very possible.
what we can do:

- use IC cascade samples
- use the actual source (it plays a huge difference)


# March 22: after graph proprocessing

observation on infection probability:

- true root > pagerank(eps=0.0) > pagerank(eps=0.5) > random
- report proba = 0.5 gives larger gap
- http://193.166.24.212/active-network-reconstruction/figs/infection-probability/

just noticed that the cascade being generated might be quite biased, need to re-run the experiment

observation on AP scores vs \#queries

- after the preprocessing, gap between prederror and random is larger on grqc
- lattice still gives strange result, this might correlate with fact that infection probabilities on infected/uninfected nodes do not separate well

# Mar 28

why prederror is bad on lattice-1028?

- sampling is noisy making inferred probability noisy
- prederror considers the uninfected/low-proba nodes, which we are less interested

one fix:

- exclude low probability nodes


# Mar 29

## edge direction for "cut" and "loop_erased"

- pointing away from root (`predmap` stores the parent)

## effect of reversing and global normalization

reversing makes a difference while normalization does not

- http://193.166.24.212:9999/notebooks/why-producing-large-trees.ipynb

# Mar 31

- 8 nodes
- 1 root
- 2 terms
- 10000000 samples
- took around 12 hours

```
cosine similarity

      (True, cut)  (True, lerw)  (lerw, cut)
       count   960.000000    960.000000   960.000000
       mean      0.996456      0.996459     0.999992
       std       0.002140      0.002136     0.000004
       min       0.987642      0.987831     0.999974
       25%       0.995206      0.995191     0.999990
       50%       0.997031      0.997036     0.999993
       75%       0.998093      0.998092     0.999996
       max       0.999848      0.999860     0.999999

Minkowsky-1 distance

      (True, cut)  (True, lerw)  (lerw, cut)
      count   960.000000    960.000000   960.000000
      mean      0.086958      0.086958     0.013373
      std       0.026215      0.026213     0.001699
      min       0.022336      0.022178     0.005653
      25%       0.067143      0.067020     0.012273
      50%       0.083389      0.083383     0.013384
      75%       0.101893      0.102235     0.014610
      max       0.173388      0.173642     0.018177
```


- 6 nodes

```
cosine similarity

       (True, cut)  (True, lerw)  (lerw, cut)
       count   480.000000    480.000000   480.000000
       mean      0.998461      0.998460     0.999998
       std       0.001626      0.001627     0.000001
       min       0.990866      0.990959     0.999994
       25%       0.997896      0.997897     0.999997
       50%       0.999064      0.999057     0.999998
       75%       0.999622      0.999621     0.999999
       max       0.999985      0.999982     1.000000

Minkowsky-1 distance

       (True, cut)  (True, lerw)  (lerw, cut)
       count   480.000000    480.000000   480.000000
       mean      0.050556      0.050583     0.003219
       std       0.028103      0.028136     0.000440
       min       0.005803      0.005986     0.001717
       25%       0.030882      0.030579     0.002920
       50%       0.045155      0.045101     0.003222
       75%       0.065110      0.065218     0.003523
       max       0.177557      0.177177     0.004375
```

# Apr 3

SIR on lattice and grqc does not give accurate result. The reason might be:

- `p(T) / pi(T)` is unbounded. It can be up to product of out degrees in the tree, leading the large variance
- [more details](https://stats.stackexchange.com/questions/76798/in-importance-sampling-why-should-the-importance-density-have-heavier-tails)
- for example, the `f/g` (product of out degrees) can be as large as `3.352242973555864e+20`


Another question is: why the result is good on complete graphs (even though small)?

- First of all, the graphs are small
- It might be each node have similar out degrees (in expectation, because they have the same number of edges and edge weights are drawn from the same distribution)

## objective function: considers inactive edges as well

the motivation: the counter-effect the effect of out degree product

- gives promising reasult: 0.99 cosine and 0.12 l1 (using only 10000 samples)
- a more reasonable approach

## practical issues

- float point underflow (in `proba_helpers.ic_cascade_probability_gt`)
  - [X] use log

# Apr 4

check AP scores comparing three different sampling objective:

- `P`
- `P'`
- `P_new`

- on lattice: `P_new > P' > P`
- on GRQC: `P' > P_new > P`

## meeting

why P gives low AP score:

- P encourages large trees because of `P / P'` is `Prod p(u)`, where `p(u)` tends to be larger than 1

# Apr 5

fixed a bug in calculating P_new, replaced `p` by `(1-p)` when considering inactive edges.

however, also observed that in `GRQC`, large trees are sampled.

The reason is, in those trees

- node out-degree tends to be large (>1)
- `Prod (1-p(u, v))` is not small because p is small (<= 0.15)
- so finally, `Prod p(u)` out-weights `Prod 1-p(u, v)`

for lattice, the result is even better for `P_new`


## population importance resampling

checked some papers:

- https://arxiv.org/pdf/0708.0711.pdf
  - works for mixture models, doesn't apply to our case
- https://www.tandfonline.com/doi/pdf/10.1198/106186004X12803?needAccess=true
  - why this `q_it`?
- [a survey](https://pdfs.semanticscholar.org/7538/2c4ac316e8326052c2baf4bd5b53016f2406.pdf)
  - do not understand why using random walker


## adaptive importance sampling

- [past, present and future](http://ieeexplore.ieee.org/document/7974876/)
  - involves updating the proposal parameters. in our case, what are the proposal parameters is not very clear.
  - I guess it's not very relevant
- http://statweb.stanford.edu/~owen/pubtalks/AdaptiveISweb.pdf


# Apri 7

- found a [plotly](https://plot.ly/python/network-graphs/) to plot networks interactively
