FROM ubuntu:20.04

## Never prompt user for choices on installation/configuration of packages
ENV DEBIAN_FRONTEND noninteractive

USER root

## define build-args
ARG API_PORT

ARG HADOOP_HOME
ARG PYTHON_HOME
ARG KERNEL_FOLDER
ARG PYTHON_VERSION
ARG HADOOP_VERSION

ENV PATH="/root/miniconda3/bin:${PATH}"
ARG PATH="/root/miniconda3/bin:${PATH}"

## update
RUN apt-get update && apt-get -yq dist-upgrade
RUN apt-get install -y locales \
    wget \
    nano \
    curl \
    zip  \
    openjdk-8-jdk

## define locales: en_US.
RUN locale-gen en_US.UTF-8
ENV LANGUAGE en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LC_ALL en_US.UTF-8
ENV LC_CTYPE en_US.UTF-8
ENV LC_MESSAGES en_US.UTF-8

## set environment variables
ENV JAVA_HOME /usr/lib/jvm/java-1.8.0-openjdk-amd64
ENV API_PORT ${API_PORT}
ENV HADOOP_HOME ${HADOOP_HOME}
ENV HADOOP_CONF_DIR ${HADOOP_HOME}/etc/hadoop
ENV PYTHON_HOME ${PYTHON_HOME}
ENV KERNEL_FOLDER ${KERNEL_FOLDER}
ENV PYTHON_VERSION ${PYTHON_VERSION}
ENV HADOOP_VERSION ${HADOOP_VERSION}
ENV PATH="${JAVA_HOME}/bin:${JAVA_HOME}/jre:${PYTHON_HOME}/bin:${HADOOP_HOME}/bin:${HADOOP_HOME}/sbin:${PATH}"


##
RUN mkdir -p ${KERNEL_FOLDER}
RUN chmod 777 -R ${KERNEL_FOLDER}



#WORKDIR /home/technical_user

## install miniconda
RUN wget \
    https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && mkdir /root/.conda \
    && bash Miniconda3-latest-Linux-x86_64.sh -b \
    && rm -f Miniconda3-latest-Linux-x86_64.sh 
RUN conda --version
RUN conda update conda
RUN conda install --yes \
    -c conda-forge -c defaults \
    python=${PYTHON_VERSION} \
    jupyter_enterprise_gateway \
    ruamel.yaml 

RUN pip install flask pyyaml

## install hadoop
RUN wget --quiet -P /tmp/ https://archive.apache.org/dist/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz
RUN tar xvf /tmp/hadoop-${HADOOP_VERSION}.tar.gz -C /tmp && \
        mv /tmp/hadoop-${HADOOP_VERSION} ${HADOOP_HOME} && \
    rm /tmp/hadoop-${HADOOP_VERSION}.tar.gz

## copy entrypoint-script & change permissions

WORKDIR home
## copy api-server programm
ADD api-server tmp/api-server
ADD docker/entrypoint.sh tmp/
RUN ["chmod", "+x", "tmp/entrypoint.sh"]
#WORKDIR ~/tmp

## expose api port
EXPOSE ${API_PORT}


ENTRYPOINT ["tmp/entrypoint.sh"]
