FROM ubuntu:19.10

ARG UID=1000
ARG GID=1000

RUN apt-get update
RUN apt-get install -y python3 python3-dev python3-pip default-jre
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

