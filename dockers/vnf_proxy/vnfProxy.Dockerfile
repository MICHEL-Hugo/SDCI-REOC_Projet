FROM node:alpine

RUN apk add --update --no-cache \
        bash \
        tcpdump \
        iperf \
        busybox-extras \
        iproute2 \
        iputils \
	    net-tools
WORKDIR /usr/app
COPY proxy.js .
RUN npm install express request body-parser fifo

ENV VIM_EMU_CMD "node proxy.js"
ENV VIM_EMU_CMD_STOP "echo 'Stopping the container...'"

CMD /bin/bash