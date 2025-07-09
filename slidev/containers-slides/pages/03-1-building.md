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
FROM alpine:latest
CMD ["echo", "hello"]
```

Lets build it. it "docker-demo"

```zsh
docker build -t docker-demo .
```

- The `-t` gives the image a name
- The `.` means "use the current directory" for context* (we may discuss this concept more later)

Start a container
```sh
docker run docker-demo
```

Check on your container

```sh
docker container ls
# uhh, not here.. why not?
```

---

### Keep it running

Common trick you may see people do for development containers:

```dockerfile
FROM alpine:latest
CMD ["sleep", "infinity"] # keep container alive for demonstration purposes
```
Note: this is not recommended in practice and is rare as a container's lifetime is almost always bound to some workload.

```bash
docker build -t docker-demo .
docker run docker-demo
```

Now, you're stuck Ctrl-C a few times to escape!


```sh
# Add --detach so you dont automatically attach to the container
docker run --detach docker-demo
```

Execute a command in a running container with `exec`


```sh
docker exec <container_id> echo "hello from container"
# clean up
docker stop <container_id>
```

---

## Naming containers

- It was a bit cumbersome to keep track of the container ID or randomly generated name.
- Instead, we can name it when we start it

```sh
docker run --name foo-bar-baz docker-demo
```

Now you should see your image in the list,

```sh
docker container ls
```

See if you can stop it.

Note: if a container is really stubborn you can `kill` it but try to avoid this.

---

## ENTRYPOINT and CMD

```dockerfile
FROM alpine:latest
# Note: base images often set ENTRYPOINT to a shell like /bin/bash or /bin/sh
# Arguments passed to ENTRYPOINT
CMD ["ls"]
```

```dockerfile
FROM alpine:latest
# Set entrypoint to be the ls command
ENTRYPOINT ["/bin/ls"]
# Pass some flags to ls
CMD ["-a", "-l"] 
```

See if you can run these example Dockerfiles.

<!--
Speaker note, some patterns users may see, make sure I touch on these:
Some slightly less obvious tricks or patterns you might see:
1. Cramming commands on one line (caching)
2. Deleting things that are created as side effects, apt cache (img size)
3. Building from source (clone, unzip, build, clean up)
	- Note: `ADD` vs. `COPY`
4. Setting permissions like `COPY --chmod=555 thing /thing`
5. Mounts in builds
6. Using build arguments
7. Multi-stage builds
-->

---

## Exercise - Cowsay

Let's try `ENTRYPOINT` and `CMD`...

1. Have `docker run myimage` get the cow to say something and `docker run myimage pwd` to run `pwd` (where `pwd` can be any shell command)
2. Have `docker run myimage Moo` get the cow to say `Moo` (where `Moo` can be any message)

Starting point:

```dockerfile
FROM debian:bookworm-slim
RUN apt update && apt install -y cowsay && rm -rf /var/lib/apt/lists/*
# Hint: cowsay is installed to /usr/games/cowsay
```

<v-click>

```dockerfile
CMD ["/usr/games/cowsay", "hi"]
```

</v-click>

<v-click>

```dockerfile
ENTRYPOINT ["/usr/games/cowsay"]
```

</v-click>
