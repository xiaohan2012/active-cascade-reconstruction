#!/bin/zsh

#SBATCH --job-name=query
#SBATCH --output=/scratch/work/xiaoh1/data-active-cascade-reconstruction/logs/query.txt
#SBATCH -n 1
#SBATCH -t 04:00:00
#SBATCH --mem-per-cpu=2500
#SBATCH --array=1-7

n=$SLURM_ARRAY_TASK_ID             # define n
line=`sed "${n}q;d" params.txt`    # get n:th line (1-indexed) of the file

# Do whatever with arrayparams.txt
python3 test.py $line
