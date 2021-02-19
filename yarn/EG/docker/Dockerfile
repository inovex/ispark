FROM ubuntu:20.04

## Never prompt user for choices on installation/configuration of packages
ENV DEBIAN_FRONTEND noninteractive

USER root

## define build-args
ARG GATEWAY_VERSION
ARG GATEWAY_PORT
ARG SPARK_HOME
ARG HADOOP_HOME
ARG PYTHON_HOME
ARG KERNEL_FOLDER
ARG PYTHON_VERSION
ARG SPARK_VERSION
ARG HADOOP_VERSION

## update
RUN apt-get update && apt-get -yq dist-upgrade
RUN apt-get install -y locales \
    wget \
    nano \
    curl \
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
ENV GATEWAY_VERSION ${GATEWAY_VERSION}
ENV GATEWAY_PORT ${GATEWAY_PORT}
ENV SPARK_HOME ${SPARK_HOME}
ENV HADOOP_HOME ${HADOOP_HOME}
ENV HADOOP_CONF_DIR ${HADOOP_HOME}/etc/hadoop
ENV PYTHON_HOME ${PYTHON_HOME}
ENV KERNEL_FOLDER ${KERNEL_FOLDER}
ENV PYTHON_VERSION ${PYTHON_VERSION}
ENV SPARK_VERSION ${SPARK_VERSION}
ENV HADOOP_VERSION ${HADOOP_VERSION}
ENV PATH="${JAVA_HOME}/bin:${JAVA_HOME}/jre:${SPARK_HOME}/bin:${SPARK_HOME}/sbin:${PYTHON_HOME}/bin:${HADOOP_HOME}/bin:${HADOOP_HOME}/sbin:${PATH}"

## install and miniconda
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /opt/miniconda.sh
RUN bash /opt/miniconda.sh -f -b -p ${PYTHON_HOME}
RUN conda install --quiet --yes python=${PYTHON_VERSION}
RUN conda update --all --quiet --yes

## install jupyter-enterprise-gateway
RUN conda install -c conda-forge --yes --quiet jupyter_enterprise_gateway=${GATEWAY_VERSION}
RUN mkdir -p ${KERNEL_FOLDER}

## install spark
RUN wget --quiet -P /tmp/ https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz
RUN tar xvf /tmp/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz -C /tmp && \
    mv /tmp/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} ${SPARK_HOME} && \
    rm /tmp/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz

## install hadoop
RUN wget --quiet -P /tmp/ https://archive.apache.org/dist/hadoop/common/hadoop-${HADOOP_VERSION}.7/hadoop-${HADOOP_VERSION}.7.tar.gz
RUN tar xvf /tmp/hadoop-${HADOOP_VERSION}.7.tar.gz -C /tmp && \
        mv /tmp/hadoop-${HADOOP_VERSION}.7 ${HADOOP_HOME} && \
    rm /tmp/hadoop-${HADOOP_VERSION}.7.tar.gz

## copy entrypoint-script & change permissions
COPY /docker/entrypoint.sh /tmp/entrypoint.sh
RUN chmod +x /tmp/entrypoint.sh

## expose gateway-port & yarn-port
EXPOSE ${GATEWAY_PORT}
EXPOSE 8088

ENTRYPOINT ["/tmp/entrypoint.sh"]