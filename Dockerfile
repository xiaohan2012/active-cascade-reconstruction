# Use an official Python runtime as a parent image
FROM tiagopeixoto/graph-tool:latest

ARG workdir=/code/
ARG repo_src=https://github.com/xiaohan2012/active-cascade-reconstruction.git

RUN echo "aaa" | passwd --stdin root

RUN mkdir -p ${workdir}

WORKDIR ${workdir}

# install pip
RUN pacman-key --refresh-keys
RUN pacman -Suy --noconfirm
RUN pacman -S python-pip  --noconfirm --needed

RUN pip install --upgrade pip

RUN (cd ${workdir}; git clone ${repo_src})
RUN (cd ${workdir}/active-cascade-reconstruction; pip install --trusted-host pypi.python.org -r requirements.txt)


