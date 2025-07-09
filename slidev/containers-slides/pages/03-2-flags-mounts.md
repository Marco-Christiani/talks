---
layout: section
---

# Docker CLI

---


## Essential Docker Commands

You will practice many of these today, no need to memorize them.

- `build`
- `run`
- `exec -it`
- `container ls/rm/etc`
- `image ls/rm/etc`
- `volume ls/rm/etc` (maybe)

---

## Container, Image, System Management

<div class="grid grid-cols-3 gap-4">

<div>

### Container Management
- `docker run`
- `docker exec`
- `docker stop`
- `docker rm` (same as `container rm`)

</div>

<div>

### Image Management
- `docker build`
- `docker pull`
- `docker push`
- `docker rmi` same as `image rm`

</div>

<div>

### System & Info
- `docker ps` (same as `container ls`)
- `docker logs`
- `docker inspect`
- `docker system prune`

</div>
</div>

Discoverability of Docker commands

```bash
docker container
docker image
docker system
```

---
layout: section
---

# Runtime Container Options

---

## Essential Docker run flags
<!--Runtime configuration-->

Several flags can be used to control influence runtime configuration of containers.

Today, we will see a few of the most useful ones to know (typically abbreviated by first letter):
- Interact with a shell: `-it` (accept stdin, allocate tty)
- Expose a port: `--port 8000:9000`
- Pass an environment variable: `--env FOO=bar`
- Name: `--name`
- Remove: `--rm`
- Detach: `--detach`
- Persisting data with mounts...
  - Mount a file/directory:
    - `--volume /path/on/host/:/path/in/container`
    - With options: `-v /thing:/thing,ro`

---


## Interact

```bash
docker run -it alpine
```

## Port Mapping

```bash
docker run --port 8000:9000 <image>
# or
docker run -p 8000:9000 <image>
```

## Environment Variables

```bash
docker run --env FOO=bar <image>
# or
docker run -e FOO=bar <image>
```

## Detach, Attach, Logs

```bash
docker run nginx # starts in foreground
docker run -d nginx # starts in background, prints container id

# Use the Docker CLI to see if its running and check the logs
docker container ls # you can see how --name is useful
docker logs nginx # Check output
docker logs -f nginx # Follow output
docker attach <container> # attach at any time if you change your mind
```

<!--
Inspecting images

docker history docker-demo

docker inspect docker-demo
-->
