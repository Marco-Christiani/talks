---
layout: section
---

# Building Images

---

## Key Dockerfile Instructions

*Apptainer has equivalents*

Cover 90% of use cases:
- `FROM` - Base image
- `RUN` - Execute commands
- `ENTRYPOINT` - Container entry command
- `CMD` - Default arguments
- `COPY` - Copy files
- `WORKDIR` - Set working directory
- `ENV` - Set environment variables


<div class="text-sm italic mt-4">
Not so hard, right? IMHO 30% of the confusion about containers is actually confusion about Linux and 20% is confusion about the shell.
</div>

---

## Exercise - Build an image

Create a file called `Dockerfile`
```dockerfile
FROM ubuntu:latest
CMD ["echo", "hello"]
```

Lets build it. Name it "docker-demo" and tag it as "yourusername-v1" for convenience.
```zsh
docker build -t docker-demo:$USER-v1 .
```

Start a container
```zsh
docker run docker-demo:$USER-v1
```

Check on your container
```zsh
docker container ls
# uhh, not here.. why not?
```

---

### Keep it running

Common trick for development containers:

```dockerfile
FROM ubuntu:latest
CMD ["sleep", "infinity"]
```

```zsh
docker build -t docker-demo:$USER-v1 .
docker run docker-demo:$USER-v1 
docker container ls
```

---

## ENTRYPOINT and CMD

```dockerfile
FROM ubuntu:latest
# note: the base ubuntu image already sets ENTRYPOINT to /bin/bash
CMD ["ls"] # arguments passed to ENTRYPOINT
```

```dockerfile
FROM ubuntu:latest
ENTRYPOINT ["/usr/bin/ls"] # set entrypoint to be the ls command
CMD ["-a", "-l"] # pass some flags to ls
```

---

## Common Patterns

Some slightly less obvious tricks or patterns you might see:
1. Cramming commands on one line (caching)
2. Deleting things that are created as side effects, apt cache (img size)
3. Building from source (clone, unzip, build, clean up)
	- Note: `ADD` vs. `COPY`
4. Setting permissions like `COPY --chmod=555 thing /thing`
5. Mounts in builds
6. Using build arguments
7. Multi-stage builds

---


## (1) Cramming commands

```dockerfile
RUN apt update && apt install -y cowsay
```

## (2) Deleting things

```dockerfile
RUN apt update && apt install -y cowsay && rm -rf /var/lib/apt/lists/* # <-- updated
```

## Exercise - Cowsay

```dockerfile
FROM ubuntu:latest
RUN apt update && apt install -y cowsay && rm -rf /var/lib/apt/lists/*
ENTRYPOINT ["/usr/games/cowsay"]
CMD ["-e", "oo", "-TU", "Moo"] # arguments passed to ENTRYPOINT
```

or

```dockerfile
ENTRYPOINT ["/bin/bash"] # In our case this is optional since ubuntu already set this
CMD ["cowsay", "-e", "oo", "-TU", "Moo"]
```


## (3) Build from Source

Install software that isn’t in your package manager:

FROM ubuntu:latest
RUN apt update && apt install -y git build-essential \
 && git clone https://github.com/example/someproj.git \
 && cd someproj && make && make install \
 && cd .. && rm -rf someproj \
 && rm -rf /var/lib/apt/lists/*


## (4) COPY --chmod

Set permissions when copying:

COPY --chmod=555 script.sh /usr/local/bin/script.sh

Useful for making scripts executable right away.

## (5) Mounts in Builds

You can mount local directories as cache or secrets during build (needs BuildKit):

# syntax=docker/dockerfile:1.4
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

Use DOCKER_BUILDKIT=1 to enable.

## (6) Build Args

Pass variables at build time (not runtime):

```dockerfile
ARG VERSION=1.0
RUN echo "Version is $VERSION"
```

Build with:

```sh
docker build --build-arg VERSION=2.0 -t demo:2.0 .
```


## (7) Multi-Stage Builds

Minimize final image size by separating build from runtime:

FROM golang:1.21 AS builder
WORKDIR /app
COPY . .
RUN go build -o myapp

FROM alpine:latest
COPY --from=builder /app/myapp /usr/local/bin/myapp
ENTRYPOINT ["myapp"]

This avoids shipping the entire Go toolchain in the final image.

