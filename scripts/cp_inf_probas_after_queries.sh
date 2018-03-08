#! /bin/zsh

datasets=(fb-msi-s0.04-o0.1)
root=figs/infection-probas-after-queries

for d in ${datasets}; do
    rm -r figs/infs-proba-${d}
    cp -r  ${root}/$d figs/infs-proba-${d}
    cp -r  ${root}/legend.png figs/infs-proba-${d}
    cp -r  ${root}/colorbar_vertical.pdf  figs/infs-proba-${d}    
done



