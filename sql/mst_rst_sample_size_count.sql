select
    dataset, infer_sampling_method, infer_n_samples, count(1)
from
    active.inference
where
    infer_sampling_method in ('mst', 'rst') and n_queries = 0
group by
    dataset, infer_sampling_method, infer_n_samples
having
    count(1) != 96
order by
    dataset, infer_sampling_method, infer_n_samples asc;
