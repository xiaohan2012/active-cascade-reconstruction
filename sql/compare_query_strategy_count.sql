SELECT
    dataset, query_method, COUNT(1)
FROM
    active.eval_per_cascade
WHERE
    n_queries=30
    AND metric_name='ap'
    AND query_sampling_method = 'naive'
    AND infer_sampling_method = 'naive'
GROUP BY
    dataset, query_method
ORDER BY
    dataset, query_method;
