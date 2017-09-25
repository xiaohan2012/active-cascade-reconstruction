import numpy as np
from graph_helpers import extract_nodes


def infection_precision_recall(preds, c, obs, return_details=False):
    """
    given set of inferred infected nodes and ground truth, return precision and recall

    Args:
    set of ints: preds, set of predicted infections (besides observations)
    np.ndarray:  c, cascade
    bool: return_details, if the corret, false_positive, false_negative should be returned

    Return:
    float: precison
    float: recall
    dict: detail of correct, fp, np keyed by the name
    """
    all_infs = set((c >= 0).nonzero()[0])
    remain_infs = all_infs - set(obs)
    preds -= set(obs)
    
    correct = preds.intersection(remain_infs)

    try:
        precision = len(correct) / len(preds)
    except ZeroDivisionError:
        assert len(correct) == 0
        precision = 0.0
        
    recall = len(correct) / len(remain_infs)

    if not return_details:
        return precision, recall
    else:
        detail = {'correct': correct,
                  'fp': preds - correct,  # is not infected but classified as infected
                  'fn': remain_infs - preds,  # is infected but classified as not infected
                  'prec': precision,
                  'rec': recall}
        
        return precision, recall, detail


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
            
    return infection_precision_recall(set(inf_nodes), c, obs, return_details=False)
