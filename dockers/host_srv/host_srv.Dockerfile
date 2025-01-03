FROM node:alpine

RUN apk add --update --no-cache \
        bash \
        tcpdump \
        iperf \
        busybox-extras \
        iproute2 \
        iputils

WORKDIR /usr/app
COPY server.js .
RUN npm install express request yargs systeminformation

CMD /bin/bash
