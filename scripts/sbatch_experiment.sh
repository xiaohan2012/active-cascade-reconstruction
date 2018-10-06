#!/bin/zsh

#SBATCH --job-name=email-univ
#SBATCH --output=/scratch/work/xiaoh1/data-active-cascade-reconstruction/logs/email-univ.txt  # %a does not work
#SBATCH --cpus-per-task 1 
#SBATCH --time 01:00:00  # per task?
#SBATCH --mem=1G
#SBATCH --array=1-384 # 96 rounds x 4 strategies

GRAPH=email-univ  # change this for new graphs

# LOG_DIR=/scratch/work/xiaoh1/data-active-cascade-reconstruction/logs/email-univ/
# if [ ! -d ${LOG_DIR} ];then 
#     mkdir -p ${LOG_DIR}
# fi

query_args_file=exp_args/query_${GRAPH}.txt
infer_args_file=exp_args/infer_${GRAPH}.txt

n=$SLURM_ARRAY_TASK_ID

query_args=`sed "${n}q;d" ${query_args_file}`
infer_args=`sed "${n}q;d" ${infer_args_file}`

eval "./singularity/exec.sh python3 query_one_round.py ${query_args}"
eval "./singularity/exec.sh python3 infer_one_round.py ${infer_args}"
