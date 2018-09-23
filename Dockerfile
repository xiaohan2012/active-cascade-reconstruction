# Use an official Python runtime as a parent image
FROM tiagopeixoto/graph-tool:latest

ARG workdir=/code/active-cascade-reconstruction

RUN mkdir -p ${workdir}

WORKDIR ${workdir}

COPY * ${workdir}/

# install pip
RUN pacman-key --refresh-keys
RUN pacman -Suy --noconfirm
RUN pacman -S python-pip  --noconfirm --needed

# upgrade pip
RUN pip install --upgrade pip

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

