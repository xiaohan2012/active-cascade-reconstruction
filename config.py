DEBUG = False

if DEBUG:
    QUERY_TIMEOUT = 3
    INFER_TIMEOUT = 3
else:
    QUERY_TIMEOUT = 3600 * 6  # in seconds
    INFER_TIMEOUT = 3600 * 6
    
