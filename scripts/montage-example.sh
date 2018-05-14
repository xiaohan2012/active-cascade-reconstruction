#! /bin/bash

montage \
    -label '%f' \
    p@k/lattice-1024-sto-msi-s0.1-o0.2.pdf p@k/infectious-sto-msi-s0.1-o0.2.pdf p@k/grqc-sto-msi-s0.1-o0.2.pdf p@k/nethept-sto-msi-s0.01-o0.2.pdf \
    l1/lattice-1024-sto-msi-s0.1-o0.2.pdf l1/infectious-sto-msi-s0.1-o0.2.pdf l1/grqc-sto-msi-s0.1-o0.2.pdf  l1/nethept-sto-msi-s0.01-o0.2.pdf \
    l2/lattice-1024-sto-msi-s0.1-o0.2.pdf l2/infectious-sto-msi-s0.1-o0.2.pdf  l2/grqc-sto-msi-s0.1-o0.2.pdf l2/nethept-sto-msi-s0.01-o0.2.pdf \
    method_legend.pdf \
    -tile 4x4 -geometry +0+0 \
    graph-x-measure.pdf
