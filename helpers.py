import numpy as np
import pickle as pkl
import errno
import os
import signal
import datetime
import psycopg2
import string
import random

from glob import glob
from scipy.spatial.distance import cdist
from functools import wraps
from config import DB_CONFIG

def load_cascades(dirname):
    for p in glob(dirname+'/*.pkl'):
        yield p, pkl.load(open(p, 'rb'))


def cascade_source(c):
    return np.nonzero((c == 0))[0][0]


def infected_nodes(c):
    return np.nonzero((c >= 0))[0]


def l1_dist(probas1, probas2):
    return cdist([probas1],
                 [probas2],
                 'minkowski', p=1.0)[0, 0]


def cascade_info(obs, c):
    print('source: {}'.format(cascade_source(c)))
    print('|casdade|: {}'.format(len(infected_nodes(c))))
    print('|observed nodes|: {}'.format(len(obs)))


class TimeoutError(Exception):
    pass


def timeout(seconds=10, error_message=os.strerror(errno.ETIME)):
    def decorator(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(error_message)

        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return wraps(func)(wrapper)
    return decorator


def sampling_weights_by_order(length):
    w = 1 / (np.arange(10) + 1)[::-1]
    w /= w.sum()
    return w


def makedir_if_not_there(d):
    if not os.path.exists(d):
        os.makedirs(d)


def get_now():
    return datetime.date.today().strftime("%Y-%m-%d %H:%M:%s")


def init_db(debug=False):
    """
    create connection, make a cursor and create the tables if needed
    """
    conn = psycopg2.connect(DB_CONFIG.connection_string)
    cursor = conn.cursor()

    cursor.execute(
        """CREATE SCHEMA IF NOT EXISTS {}""".format(DB_CONFIG.schema)
    )
    sqls_to_execute = (
        DB_CONFIG.query_table_creation,
        DB_CONFIG.inference_table_creation,
        DB_CONFIG.eval_table_creation
    )
    for sql in sqls_to_execute:
        cursor.execute(sql)
    if debug:
        # conn.set_trace_callback(print)
        pass
    return conn, cursor


def get_query_result(
        cursor,
        dataset,
        c_id,
        query_method,
        sampling_method,
        n_samples,
        n_queries,
        root_sampler,
        min_proba,
        fields=['1']
):
    cursor.execute(
        """
        SELECT
            {fields_str}
        FROM
            {schema}.{table_name}
        WHERE
            dataset=%s
            AND cascade_id=%s
            AND query_method=%s
            AND sampling_method=%s
            AND n_samples=%s
            AND n_queries=%s
            AND root_sampler=%s
            AND pruning_proba=%s
        """.format(
            schema=DB_CONFIG.schema,
            fields_str=', '.join(fields),
            table_name=DB_CONFIG.query_table_name
        ),
        (
            dataset,
            c_id,
            query_method,
            sampling_method,
            n_samples,
            n_queries,
            root_sampler,
            min_proba
        )
    )
    
    return cursor.fetchone()


def get_inference_result(
        cursor,
        dataset,
        c_id,
        query_method,
        sampling_method,
        n_samples,
        n_queries,
        root_sampler,
        min_proba,
        infer_sampling_method,
        infer_n_samples,
        every,
        fields=['1']
):
    cursor.execute(
        """
        SELECT
            {fields_str}
        FROM
            {schema}.{table_name}
        WHERE
            dataset=%s
            AND cascade_id=%s
            AND query_method=%s
            AND query_sampling_method=%s
            AND query_n_samples=%s
            AND n_queries=%s
            AND root_sampler=%s
            AND pruning_proba=%s
            AND infer_sampling_method=%s
            AND infer_n_samples=%s
            AND every=%s
        """.format(
            schema=DB_CONFIG.schema,
            fields_str=', '.join(fields),
            table_name=DB_CONFIG.inference_table_name
        ),
        (
            dataset,
            c_id,
            query_method,
            sampling_method,
            n_samples,
            n_queries,
            root_sampler,
            min_proba,
            infer_sampling_method,
            infer_n_samples,
            every
        )
    )
    
    return cursor.fetchone()


def random_str(N=8):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(N))
