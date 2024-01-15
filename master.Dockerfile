FROM alpine:latest

RUN apk update && apk add \
    tor python3 py3-pip py3-flask \
    --update-cache --repository http://dl-3.alpinelinux.org/alpine/edge/testing/ \
    && rm -rf /var/cache/apk/*

COPY ./torrc-master /etc/tor/torrc

RUN mkdir /app
WORKDIR /app
COPY ./master.sh .
RUN chmod +x /app/master.sh

COPY ./server.py .

CMD ["sh", "/app/master.sh"]
