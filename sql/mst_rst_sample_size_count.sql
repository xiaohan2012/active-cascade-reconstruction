select
    dataset, infer_sampling_method, infer_n_samples, count(1)
from
    active.inference
where
    infer_sampling_method in ('mst', 'rst', 'rrs') and n_queries = 0 and infer_n_samples <= 2560
group by
    dataset, infer_sampling_method, infer_n_samples
-- having
--     count(1) != 96
order by
    dataset, infer_sampling_method, infer_n_samples asc;
