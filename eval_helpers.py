import numpy as np
import math
import os
import pickle as pkl
from copy import copy
from tqdm import tqdm

from graph_helpers import extract_nodes
from helpers import infected_nodes
from tree_stat import EPS
from sklearn.metrics import precision_score, average_precision_score, log_loss



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


def precision_at_k(y, probas, k):
    pred_idx = np.argsort(probas)[::-1][:k]
    return precision_score(y[pred_idx], np.ones(k))


def precision_at_cascade_size(y, probas):
    k = (y > 0).sum()
    return precision_at_k(y, probas, k)


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


def aggregate_scores_over_cascades_by_methods(
        cascades,
        method_labels,
        query_dir_ids,
        inf_dir_ids,
        n_queries,
        inf_result_dirname,
        query_dirname,
        eval_method,
        eval_with_mask,
        iter_callback=None,
        every=1
):
    """
    each element in `method_labels` uniquely identifies one experiment

    Returns: method_name -> [n_experiments x n_queries]
    """
    assert len(method_labels) == len(query_dir_ids) == len(inf_dir_ids)
    # dict of key -> [n_experiments x n_queries]
    scores_by_method = {}
    for l in method_labels:
        scores_by_method[l] = []
    
    c_paths = []  # track the order
    for c_path, tpl in tqdm(cascades):
        obs, c = tpl[:2]
        
        obs = set(obs)
        c_paths.append(c_path)
        infected = (c >= 0).nonzero()[0]
        # infected_set = set(infected)
        # print('infection size', len(infected_set))
        # labels for nodes, 1 for infected, 0 for uninfected
        y_true = np.zeros((len(c), ))
        y_true[infected] = 1
        
        for method_label, query_dir, inf_dir in zip(method_labels, query_dir_ids, inf_dir_ids):
            cid = os.path.basename(c_path).split('.')[0]
            # load infection probabilities
            inf_probas_path = os.path.join(
                inf_result_dirname,
                inf_dir,
                '{}.pkl'.format(cid))
            print('processing id ', cid)
            try:
                inf_probas_list = pkl.load(open(inf_probas_path, 'rb'))

                n_probas_to_show = int(n_queries / every)
                inf_probas_list = inf_probas_list[:n_probas_to_show+1]
        
            except EOFError:
                print('**EOFError, inf_probas_path=', inf_probas_path)
                print("**WARNING**: ignore corrupted file")
                continue
            except IOError:
                print('WARNING**: ignore non-existing file: ', inf_probas_path)
                continue

            # load queries
            query_path = os.path.join(
                query_dirname, query_dir, '{}.pkl'.format(cid))

            queries = pkl.load(open(query_path, 'rb'))[0]
            queries = queries[:n_queries]

            scores = get_scores_by_queries(
                queries,
                inf_probas_list,
                c, obs,
                eval_method,
                every=every,
                eval_with_mask=eval_with_mask,
                iter_callback=iter_callback
            )
            
            scores_by_method[method_label].append(scores)
    for method_label in method_labels:
        print('{method}: collected {count} rounds'.format(
            method=method_label,
            count=len(scores_by_method[method_label])
        ))
        
    return scores_by_method


def eval_probas(c, X, probas):
    infected = infected_nodes(c)
    y_true = np.zeros((len(c), ))
    y_true[infected] = 1
    X_set = set(X)
    mask = np.array([(i not in X_set) for i in range(len(c))])
    
    ap_score = average_precision_score(y_true[mask], probas[mask])
    p_score = precision_at_cascade_size(y_true[mask], probas[mask])
    return {'ap': ap_score, 'pk': p_score}


def mean_average_precision(y_true, p_pred):
    idx = np.argsort(p_pred)[::-1]
    y = y_true[idx]
    map_score = np.mean([y[:i+1].sum() / (i+1) for i in y.nonzero()[0]])
    return map_score


def mean_reciprical_rank(y_true, p_pred):
    idx = np.argsort(p_pred)[::-1]
    # p = p_pred[idx]
    y = y_true[idx]
    k = y_true.sum()

    scores = 1 / (1 + (y == 1).nonzero()[0])
    M = 1 / np.arange(1, k+1)
    return scores.sum() / M.sum()


def get_score(eval_method, y_true, y_pred):
    if eval_method == 'ap':
        try:
            score = average_precision_score(y_true, y_pred)
        except FloatingPointError:
            score = np.nan                        
    elif eval_method == 'l1':
        score = np.abs(y_true - y_pred).sum()
    else:
        raise ValueError('not valid eval method {}'.format(eval_method))
    return score


def get_scores_by_queries(qs, probas, c, obs,
                          eval_method,
                          every=1,
                          eval_with_mask=True,
                          iter_callback=None,
                          **kwargs):
    inf_nodes = set(infected_nodes(c))
    y_true = np.zeros((len(c), ))
    y_true[infected_nodes(c)] = 1
    obs_inc = copy(set(obs))

    inf_obs = set(obs)
    uninf_obs = set()

    def get_mask(obs_inc):
        if eval_with_mask:
            mask = np.array([(node not in obs_inc) for node in range(len(c))])
        else:
            mask = np.ones(len(c), dtype=np.bool)
        return mask
    
    scores_list = []

    # the score without any queries
    mask = get_mask(obs_inc)
    if len(probas) > 0:
        inf_probas = probas[0]
        scores_list.append(
            get_score(
                eval_method,
                y_true[mask],
                inf_probas[mask]
            )
        )
    else:
        scores_list.append(np.nan)

    for i_iter, query in enumerate(qs):
        if c[query] == -1:
            uninf_obs.add(query)
        else:
            inf_obs.add(query)
            
        obs_inc.add(query)

        if i_iter % every == 0:    
            proba_index = int(i_iter / every)
            try:
                inf_probas = probas[proba_index + 1]  # offset +1 because of the initial probas
            except IndexError:
                print('inf_probas missing, append np.nan')
                scores_list.append(np.nan)
                continue

            if callable(iter_callback):
                iter_callback(inf_probas, inf_obs, uninf_obs)

            # mask out the observed nodes
            mask = get_mask(obs_inc)
            
            score = get_score(
                eval_method,
                y_true[mask],
                inf_probas[mask]
            )
            scores_list.append(score)
    return scores_list
