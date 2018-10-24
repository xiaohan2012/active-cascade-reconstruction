DEBUG = False

ONE_HOUR_IN_SECS = 3600

if DEBUG:
    QUERY_TIMEOUT = 60
    INFER_TIMEOUT = 60
else:
    QUERY_TIMEOUT = ONE_HOUR_IN_SECS * 1  # multiply by hours
    INFER_TIMEOUT = ONE_HOUR_IN_SECS * 1
    
DATA_ROOT_DIR = '/experiment'
TMP_DIR = '/scratch/work/xiaoh1/data-active-cascade-reconstruction/tmp'

class DB_CONFIG:
    """
    configuration for the database-related stuff
    """
    if DEBUG:
        dbpath = '{}/outputs/result_debug.db'.format(DATA_ROOT_DIR)
    else:
        dbpath = '{}/outputs/result.db'.format(DATA_ROOT_DIR)
    
    query_table_name = 'queries'
    query_table_creation = """
    CREATE TABLE IF NOT EXISTS {table_name}
    (
        dataset TEXT,
        cascade_id INTEGER, 
        query_method TEXT,
        sampling_method TEXT,
        n_samples INTEGER,
        n_queries INTEGER,
        root_sampler TEXT,
        pruning_proba REAL,

        queries BLOB,

        time_elapsed REAL,
        created_at TEXT
    )
    """.format(
        table_name=query_table_name
    )
    
    inference_table_name = 'inference'
    inference_table_creation = """
    CREATE TABLE IF NOT EXISTS {table_name}
    (
        dataset TEXT,
        cascade_id INTEGER, 
        query_method TEXT,
        query_sampling_method TEXT,
        query_n_samples INTEGER,
        n_queries INTEGER,
        root_sampler TEXT,
        pruning_proba REAL,
        infer_sampling_method TEXT,
        infer_n_samples INTEGER,
        every INTEGER,

        probas BLOB,

        time_elapsed REAL,
        created_at TEXT
    )
    """.format(
        table_name=inference_table_name
    )
    
    eval_table_name = 'eval_per_cascade'
    eval_table_creation = """
    CREATE TABLE IF NOT EXISTS {table_name}
    (
        dataset TEXT,
        cascade_id INTEGER, 
        query_method TEXT,
        query_sampling_method TEXT,
        query_n_samples INTEGER,
        n_queries INTEGER,
        root_sampler TEXT,
        pruning_proba REAL,
        infer_sampling_method TEXT,
        infer_n_samples INTEGER,
        every INTEGER,

        metric_name TEXT,
        metric_score REAL,
        masked INTEGER,

        time_elapsed REAL,
        created_at TEXT
    )
    """.format(
        table_name=eval_table_name
    )
