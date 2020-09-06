FROM ubuntu:20.04

ARG UID=1000
ARG GID=1000

RUN apt-get update
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Budapest
RUN apt-get install -y python3 python3-pip default-jre && rm -rf /var/lib/apt/lists/*
RUN groupadd -r -g $GID minecraft && useradd -r -m -u $UID -g minecraft minecraft

RUN mkdir /servers
RUN chown -R minecraft:minecraft /servers
COPY --chown=minecraft:minecraft ./scripts /scripts
WORKDIR /scripts
RUN pip3 install -r requirements.txt

EXPOSE 25500-25600

USER minecraft
RUN touch /scripts/mcst.log
CMD ["tail", "-f", "/scripts/mcst.log"]

