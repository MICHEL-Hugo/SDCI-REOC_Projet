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
COPY gateway.js .
RUN npm install express request yargs systeminformation 

ENV VIM_EMU_CMD "node gateway.js --local_ip '10.0.0.12' --local_port 8282 --local_name 'proxy' --remote_ip '10.0.0.10' --remote_port 8282 --remote_name 'gi'"
ENV VIM_EMU_CMD_STOP "echo 'Stopping the container...'"

CMD /bin/bash
