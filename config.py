DEBUG = False

ONE_HOUR_IN_SECS = 3600

if DEBUG:
    QUERY_TIMEOUT = 3
    INFER_TIMEOUT = 3
else:
    QUERY_TIMEOUT = ONE_HOUR_IN_SECS * 1  # multiply by hours
    INFER_TIMEOUT = ONE_HOUR_IN_SECS * 1
    
DATA_ROOT_DIR = '/experiment'
