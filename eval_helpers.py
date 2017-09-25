import numpy as np


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


def top_k_infection_precision_recall(inf_probas, c, obs, k):
    """
    take the top k infections ordered by inf_probas, from high to low

    and then calculate the precision and recall w.r.t to obs
    """
    inf_nodes = set(np.argsort(inf_probas)[::-1][:k])
    return infection_precision_recall(inf_nodes, c, obs, return_details=False)
