FROM node:alpine

RUN apk add --update --no-cache \
        bash \
        tcpdump \
        iperf \
        busybox-extras \
        iproute2 \
        iputils

WORKDIR /usr/app
COPY device2.js .
RUN npm install express request yargs

CMD /bin/bash
