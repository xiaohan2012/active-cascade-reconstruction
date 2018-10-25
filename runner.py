"""
run an experiment suite specified by the name
"""
import os
import argparse
import tempfile
from helpers import random_str
from config import TMP_DIR

def gen_sbatch_string(
        job_name,
        hours_per_job,
        minutes_per_job,
        n_jobs,
        logfile_name,
        query_file_name,
        infer_file_name,
        eval_file_name,
        n_jobs_at_a_time=800,
):
    return """#!/bin/zsh

#SBATCH --job-name={job_name}
#SBATCH --output={logfile_name}  # %a does not work
#SBATCH --cpus-per-task 1 
#SBATCH --time {hours_per_job}:{minutes_per_job}:00  # per task?
#SBATCH --mem=1G
#SBATCH --array=1-{n_jobs}%{n_jobs_at_a_time}

query_args_file={query_file_name}
infer_args_file={infer_file_name}
eval_args_file={eval_file_name}

n=$SLURM_ARRAY_TASK_ID

query_args=`sed "${{n}}q;d" ${{query_args_file}}`
infer_args=`sed "${{n}}q;d" ${{infer_args_file}}`
eval_args=`sed "${{n}}q;d" ${{eval_args_file}}`

eval "./singularity/exec.sh python3 query_one_round.py ${{query_args}}"
eval "./singularity/exec.sh python3 infer_one_round.py ${{infer_args}}"
eval "./singularity/exec.sh python3 evaluate_one_round.py ${{eval_args}}"
""".format(
    job_name=job_name,
    hours_per_job=str(hours_per_job).zfill(2),
    minutes_per_job=str(minutes_per_job).zfill(2),
    n_jobs_at_a_time=n_jobs_at_a_time,
    n_jobs=n_jobs,
    logfile_name=logfile_name,
    query_file_name=query_file_name,
    infer_file_name=infer_file_name,
    eval_file_name=eval_file_name
)

def gen_tmp_file(prefix="", suffix=""):
    path = os.path.join(TMP_DIR, prefix + random_str() + suffix)
    return open(path, 'a')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--name',
        required=True,
        help='the experiment name'
    )

    parser.add_argument(
        '-d',
        '--debug',
        action='store_true',
        help="debug mode or not"
    )

    args = parser.parse_args()
    iter_configs = getattr(__import__('exp_configs'), args.name)
    
    configs = list(iter_configs())
    print(args.debug)
    if args.debug:
        for config in configs:
            config.n_rounds = 1
            config.arg_suffix = '--verbose --debug'
            config.print_query_params(prefix="./singularity/exec.sh python3 query_one_round.py ")
            print('\n')
            config.print_infer_params(prefix="./singularity/exec.sh python3 infer_one_round.py ")
            print('\n')
            config.print_eval_params(prefix="./singularity/exec.sh python3 evaluate_one_round.py ")
            print('\n')            
    else:
        query_params_file = gen_tmp_file(prefix=args.name + '_query_')
        infer_params_file = gen_tmp_file(prefix=args.name + '_infer_')
        eval_params_file = gen_tmp_file(prefix=args.name + '_eval_')
        log_file = gen_tmp_file(prefix=args.name + '_log_')
        sbatch_script_file = gen_tmp_file(prefix=args.name + '_sbatch_')    
        
        print('writing query params to {}'.format(query_params_file.name))
    
        for config in configs:
            config.print_query_params(fileobj=query_params_file)
        query_params_file.close()
        
        print('writing infer params to {}'.format(infer_params_file.name))
        for config in configs:
            config.print_infer_params(fileobj=infer_params_file)
        infer_params_file.close()

        print('writing eval params to {}'.format(eval_params_file.name))
        for config in configs:
            config.print_eval_params(fileobj=eval_params_file)
        eval_params_file.close()

        n_jobs = sum(c.n_jobs for c in configs)
        sbatch_string = gen_sbatch_string(
            args.name,
            config.hours_per_job,
            config.minutes_per_job,
            n_jobs,
            log_file.name,
            query_params_file.name,
            infer_params_file.name,
            eval_params_file.name
        )
        print("sbatch commands as follows\n{}\n".format('='*10))
        print(sbatch_string)
        print("{}\n".format('='*10))

        print('saved to {}'.format(sbatch_script_file.name))
        sbatch_script_file.write(sbatch_string)

        sbatch_script_file.close()
        log_file.close()
