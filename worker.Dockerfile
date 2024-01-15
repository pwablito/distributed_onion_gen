FROM alpine:latest as builder

RUN apk add --no-cache autoconf build-base gcc git libsodium-dev make
RUN git clone https://github.com/cathugger/mkp224o.git mkp224o
WORKDIR /mkp224o
RUN ./autogen.sh
ARG FILTERS=--enable-intfilter=64
ARG FLAGS=--enable-donna
RUN ./configure $FLAGS $FILTERS
RUN make

RUN cp /mkp224o/mkp224o /usr/bin/.
RUN apk update && apk add \
    tor python3 py3-pip \
    --update-cache --repository http://dl-3.alpinelinux.org/alpine/edge/testing/ \
    && rm -rf /var/cache/apk/*

RUN python3 -m pip install --break-system-packages 'requests[socks]'
COPY ./torrc-worker /etc/tor/torrc

RUN mkdir /app
WORKDIR /app
COPY ./worker.sh .
COPY ./worker.py .
RUN chmod +x /app/worker.sh

CMD ["sh", "/app/worker.sh"]
