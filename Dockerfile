FROM ubuntu:14.04
MAINTAINER Jim Rybarski jim@rybarski.com

RUN apt-get update && apt-get install -y \
  git \
  gcc \
  gfortran \
  build-essential \
  python2.7 \
  python2.7-dev \
  python-pip \
  python-virtualenv \
  liblapack-dev \
  libblas-dev \
  libatlas-dev \
  tk \
  tk-dev \ 
  python-tk \
  mencoder \ 
  libhdf5-dev \
  libfftw3-dev

COPY . /opt/
RUN pip install Cython
RUN pip install numpy
RUN pip install scipy
RUN pip install numexpr
RUN pip install -r /opt/requirements.txt
RUN pip install -r /opt/external_requirements.txt

WORKDIR /opt/nd2reader
RUN python setup.py install
WORKDIR /opt/
RUN mkdir -p /var/log
RUN touch /var/log/fylm.log
RUN touch /var/log/fylm_error.log
RUN chmod -R 777 /var/log
CMD /bin/bash