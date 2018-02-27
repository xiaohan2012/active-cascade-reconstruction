import numpy as np
import os
import pickle as pkl
from copy import copy
from sklearn.metrics import average_precision_score
from tqdm import tqdm

from graph_helpers import extract_nodes


class TooSmallCascadeError(Exception):
    pass


def infection_precision_recall(preds, c, obs):
    """
    given set of inferred infected nodes and ground truth, return precision and recall

    Args:
    set of ints: preds, set of predicted infections (besides observations)
    np.ndarray:  c, cascade
    bool: return_details, if the corret, false_positive, false_negative should be returned

    Return:
    float: precison
    float: recall
    """
    all_infs = set((c >= 0).nonzero()[0])
    remain_infs = all_infs - set(obs)
    preds -= set(obs)
    
    correct = preds.intersection(remain_infs)

    precision = len(correct) / len(preds)
    recall = len(correct) / len(remain_infs)

    return precision, recall


def top_k_infection_precision_recall(g, inf_probas, c, obs, k):
    """
    take the top k infections ordered by inf_probas, from high to low

    and then calculate the precision and recall w.r.t to obs
    """
    # rank and exclude the observed nodes first
    n2proba = {n: proba for n, proba in zip(extract_nodes(g), inf_probas)}
    inf_nodes = []
    for i in sorted(n2proba, key=n2proba.__getitem__, reverse=True):
        if len(inf_nodes) == k:
            break
        if i not in obs:
            inf_nodes.append(i)
            
    return infection_precision_recall(set(inf_nodes), c, obs)


def aggregate_scores_over_cascades_by_methods(cascades, methods,
                                              n_queries,
                                              inf_result_dirname, query_dirname):
    """
    Returns: method_name -> [n_experiments x n_queries]
    """

    # dict of key -> [n_experiments x n_queries]
    scores_by_method = {}
    for method in methods:
        scores_by_method[method] = []
    
    c_paths = []  # track the order
    for c_path, (obs, c) in tqdm(cascades):
        
        obs = set(obs)
        c_paths.append(c_path)
        infected = (c >= 0).nonzero()[0]
        # infected_set = set(infected)
        # print('infection size', len(infected_set))
        # labels for nodes, 1 for infected, 0 for uninfected
        y_true = np.zeros((len(c), ))
        y_true[infected] = 1
        
        for method in methods:
            cid = os.path.basename(c_path).split('.')[0]
            inf_probas_path = os.path.join(
                inf_result_dirname,
                method,
                '{}.pkl'.format(cid))
            inf_probas_list = pkl.load(open(inf_probas_path, 'rb'))
            # print('method', method)
            # print('inf_probas_list', inf_probas_list)
                    
            query_path = os.path.join(
                query_dirname, method, '{}.pkl'.format(cid))

            # print('query_path', query_path)
            queries = pkl.load(open(query_path, 'rb'))[0]
            scores = []
            obs_inc = copy(obs)
            for inf_probas, query, _ in zip(inf_probas_list, queries, range(n_queries)):
                obs_inc.add(query)
                # need to mask out the observations
                # use precision score
                mask = np.array([(i not in obs_inc) for i in range(len(c))])
                try:
                    score = average_precision_score(y_true[mask], inf_probas[mask])
                except FloatingPointError:
                    # in this case, there is no positive data points left in y_true[mask]
                    # therefore, precision is always zero
                    # ignore this cascade because it's too small
                    raise TooSmallCascadeError from FloatingPointError
                scores.append(score)

            scores_by_method[method].append(scores)
            
    return scores_by_method
