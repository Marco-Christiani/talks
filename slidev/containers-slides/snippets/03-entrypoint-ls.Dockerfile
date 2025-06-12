FROM ubuntu:latest
ENTRYPOINT ["/usr/bin/ls"]
CMD ["-a", "-l"]
