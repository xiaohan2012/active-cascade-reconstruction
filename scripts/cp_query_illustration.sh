#! /bin/zsh

datasets=(grqc lattice-1024 p2p fb)

for d in ${datasets}; do
    rm -r figs/query-illustration-${d}
    cp -r  figs/why-random-is-good/${d}-msi-s0.04-o0.1/prediction_error_best figs/query-illustration-${d}
done

cp -r  figs/why-random-is-good/grqc-msi-s0.04-o0.1/legend.png figs/query-illustration-legend.png

