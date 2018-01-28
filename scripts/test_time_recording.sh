#! /bin/zsh

python3 generate_queries.py  \
	-g grqc \
	-q prediction_error \
        -p 0.2 \
	-n 10 \
	-s 250 \
	-m loop_erased  \
	-c cascade/grqc-msi-s0.16-o0.1      \
	-d outputs/queries/test \
	--debug --verbose
