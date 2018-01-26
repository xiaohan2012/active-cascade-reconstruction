#! /bin/zsh

python3 generate_queries.py \
	-g grqc \
	-q prediction_error \
	-n 100 \
	-s 250 \
	-m loop_erased \
	-c cascade/bug-fix/ \
	-d outputs/queries/grqc/test \
	--debug --verbose
