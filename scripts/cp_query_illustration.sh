#! /bin/zsh

rm -r figs/query-illustration-grqc
rm -r figs/query-illustration-lattice

cp -r  figs/why-random-is-good/grqc-msi-s0.04-o0.1/prediction_error_best figs/query-illustration-grqc
cp -r  figs/why-random-is-good/lattice-1024-msi-s0.04-o0.1/prediction_error_best figs/query-illustration-lattice
cp -r  figs/why-random-is-good/grqc-msi-s0.04-o0.1/legend.png figs/query-illustration-legend.png

