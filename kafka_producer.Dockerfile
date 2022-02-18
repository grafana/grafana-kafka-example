FROM ubuntu:21.04 as ubuntu_base

ENV HOME_DIR="/home/test"
RUN mkdir ${HOME_DIR}

RUN apt-get update && apt-get install -y --no-install-recommends \
    vim unzip wget curl net-tools iputils-ping ca-certificates \
    python3 python3-pip && \
    pip3 install confluent_kafka

WORKDIR ${HOME_DIR}

COPY kafka/ $HOME_DIR/kafka

CMD /bin/bash
