FROM ubuntu:latest
RUN apt update && apt install -y git build-essential \
 && git clone https://github.com/example/someproj.git \
 && cd someproj && make && make install \
 && cd .. && rm -rf someproj \
 && rm -rf /var/lib/apt/lists/*
