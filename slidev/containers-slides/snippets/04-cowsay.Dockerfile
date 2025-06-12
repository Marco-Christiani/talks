FROM ubuntu:latest
RUN apt update && apt install -y cowsay && rm -rf /var/lib/apt/lists/*
ENTRYPOINT ["/usr/games/cowsay"]
CMD ["-e", "oo", "-TU", "Moo"]

