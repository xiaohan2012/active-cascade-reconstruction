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
    connection_string = 'dbname=postgres user=xiaoh1 host=10.10.254.21'
    
    if DEBUG:
        schema = 'active_dbg'
    else:
        schema = 'active'
        
    query_table_name = 'queries'
    query_table_creation = """
    CREATE TABLE IF NOT EXISTS {schema}.{table_name}
    (
        dataset TEXT,
        cascade_id INTEGER, 
        query_method TEXT,
        sampling_method TEXT,
        n_samples INTEGER,
        n_queries INTEGER,
        root_sampler TEXT,
        pruning_proba NUMERIC,

        queries BYTEA,

        time_elapsed REAL,
        created_at TEXT
    )
    """.format(
        table_name=query_table_name,
        schema=schema
    )
    
    inference_table_name = 'inference'
    inference_table_creation = """
    CREATE TABLE IF NOT EXISTS {schema}.{table_name}
    (
        dataset TEXT,
        cascade_id INTEGER, 
        query_method TEXT,
        query_sampling_method TEXT,
        query_n_samples INTEGER,
        n_queries INTEGER,
        root_sampler TEXT,
        pruning_proba NUMERIC,
        infer_sampling_method TEXT,
        infer_n_samples INTEGER,
        every INTEGER,

        probas BYTEA,

        time_elapsed REAL,
        created_at TEXT
    )
    """.format(
        table_name=inference_table_name,
        schema=schema
    )
    
    eval_table_name = 'eval_per_cascade'
    eval_table_creation = """
    CREATE TABLE IF NOT EXISTS {schema}.{table_name}
    (
        dataset TEXT,
        cascade_id INTEGER, 
        query_method TEXT,
        query_sampling_method TEXT,
        query_n_samples INTEGER,
        n_queries INTEGER,
        root_sampler TEXT,
        pruning_proba NUMERIC,
        infer_sampling_method TEXT,
        infer_n_samples INTEGER,
        every INTEGER,

        metric_name TEXT,
        metric_scores BYTEA,
        masked BOOLEAN,

        time_elapsed REAL,
        created_at TEXT
    )
    """.format(
        table_name=eval_table_name,
        schema=schema
    )
