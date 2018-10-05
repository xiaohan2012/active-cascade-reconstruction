# Use an official Python runtime as a parent image
FROM tiagopeixoto/graph-tool:latest

ARG codedir=/code
ARG workdir=${codedir}/active-cascade-reconstruction
ARG repo_src=https://github.com/xiaohan2012/active-cascade-reconstruction.git
ARG rand_stt_src=https://github.com/xiaohan2012/random_steiner_tree.git

RUN mkdir -p ${workdir}

WORKDIR ${workdir}

# install packages
RUN pacman-key --refresh-keys
RUN pacman -Suy --noconfirm
RUN pacman -S emacs zsh python-pip  --noconfirm --needed

RUN pip install --upgrade pip

RUN (cd ${codedir}; git clone ${repo_src})
RUN (cd ${workdir}; pip install --trusted-host pypi.python.org -r requirements.txt)
RUN (cd ${workdir}; python setup.py build_ext --inplace)

# install random_steiner_tree
RUN (cd ${codedir}; git clone -b arc  ${rand_stt_src}; cd ./random_steiner_tree; python3.6 setup.py install)

# git stuff
# should be included into a bash file
RUN git config --global user.email "xiaohan2012@gmail.com"
RUN git config --global user.name "Han Xiao"

RUN (alias pytest="pytest -W ignore")

# directories to store experiment files
# this is useful for Triton
RUN (mkdir -p /experiment/graphs; mkdir -p /experiment/cascades; mkdir -p /experiment/outputs;)

CMD ["cd", "${workdir}"]