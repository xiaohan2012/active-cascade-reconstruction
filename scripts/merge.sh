#! /bin/zsh

cd $1

montage \
    lattice-100-msi-s0.25-o0.25-omuniform.pdf \
    infectious-msi-s0.1-o0.1-omuniform.pdf \
    email-univ-msi-s0.025-o0.1-omuniform.pdf \
    student-msi-s0.025-o0.1-omuniform.pdf  \
    -geometry 1024x1024 \
    -tile 4x1 all.pdf
