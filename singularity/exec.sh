#! /bin/zsh

<<<<<<< HEAD
WRKDIR=/scratch/work/xiaoh1
SRC_DIR=$WRKDIR/data-active-cascade-reconstruction
=======

WRKDIR=/scratch/work/xiaoh1
SRC_DIR=$WRKDIR/data-active-cascade-reconstruction
# TGT_DIR=/home/xiaoh1/code/active-cascade-reconstruction
>>>>>>> 854f83b7443de08b8a2303eea77890982818b72c
TGT_DIR=/experiment

bind_paths="${SRC_DIR}/cascades:${TGT_DIR}"

bind_paths="${SRC_DIR}/graphs:${TGT_DIR}/graphs"
bind_paths="${bind_paths},${SRC_DIR}/outputs:${TGT_DIR}/outputs"
bind_paths="${bind_paths},${SRC_DIR}/cascades:${TGT_DIR}/cascades"

set -x
singularity exec -B ${bind_paths}  ${WRKDIR}/.singularity_cache/active-cascade-reconstruction.simg $@
