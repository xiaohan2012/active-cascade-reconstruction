all: compile

compile:
	python3 setup.py build_ext --inplace
