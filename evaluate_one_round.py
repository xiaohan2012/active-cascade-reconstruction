import os
import argparse
import pickle as pkl
import time
from arg_helpers import (
    add_input_args,
    add_query_method_args,
    add_inference_args,
    add_eval_args
)
from helpers import (
    init_db,
    get_query_result,
    get_inference_result,
    get_now
)
from eval_helpers import get_scores_by_queries
from config import DB_CONFIG

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    add_input_args(parser)
    add_query_method_args(parser)
    add_inference_args(parser)
    add_eval_args(parser)

    args = parser.parse_args()
    
    conn, cursor = init_db(True)

    c_id = int(os.path.basename(args.cascade_path).split('.')[0])
    
    query_result = get_query_result(
        cursor,
        args.dataset,
        c_id,
        args.query_method,
        args.query_sampling_method,
        args.query_n_samples,
        args.n_queries,
        args.root_sampler,
        args.min_proba,
        fields=['queries']
    )
    if query_result is None:
        raise IOError('query result not available')
    
    queries = pkl.loads(query_result[0])[0]

    inf_result = get_inference_result(
        cursor,
        args.dataset,
        c_id,
        args.query_method,
        args.query_sampling_method,
        args.query_n_samples,
        args.n_queries,
        args.root_sampler,
        args.min_proba,
        args.inference_sampling_method,
        args.inference_n_samples,
        args.infer_every,
        fields=['probas']
    )
    if inf_result is None:
        raise IOError('inf result not available')

    probas = pkl.loads(inf_result[0])

    obs, c = pkl.load(open(args.cascade_path, 'rb'))

    c_id = int(os.path.basename(args.cascade_path).split('.')[0])

    stime = time.time()
    
    scores = get_scores_by_queries(
        queries,
        probas,
        c, obs,
        args.metric_name,
        every=args.infer_every,
        eval_with_mask=args.eval_with_mask,
        iter_callback=None
    )
    
    data_to_insert = dict(
        dataset=args.dataset,
        cascade_id=c_id,
        query_method=args.query_method,
        query_sampling_method=args.query_sampling_method,
        query_n_samples=args.query_n_samples,
        n_queries=args.n_queries,
        root_sampler=args.root_sampler,
        pruning_proba=args.min_proba,
        infer_sampling_method=args.inference_sampling_method,
        infer_n_samples=args.inference_n_samples,
        every=args.infer_every,

        metric_name=args.metric_name,
        metric_score=pkl.dumps(scores),
        masked=int(args.eval_with_mask),

        time_elapsed=time.time() - stime,
        created_at=get_now()
    )

    cursor.execute(
        """
    INSERT INTO
        {table_name} ({fields})
    VALUES
        ({placeholders})
    """.format(
        table_name=DB_CONFIG.eval_table_name,
        fields=', '.join(data_to_insert.keys()),
        placeholders=', '.join(['?'] * len(data_to_insert))
    ),
        tuple(data_to_insert.values())
    )
    conn.commit()
    conn.close()
