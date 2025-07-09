---
layout: section
---

# Persisting data

---

# Mounts and Volumes

1. mounts: Allow container access to a folder
2. volumes: Give it a kind of virtual disk managed by docker somewhere else


<br>


<div class="grid grid-cols-2 gap-4">

<div>

### Bind Mounts
- Direct mapping to host filesystem
- Great for development
- Less isolation

```bash
# Basic mount
docker run --volume /host/path:/container/path

# With options
docker run -v /host/path:/container/path:ro
```

</div>

<div>

### Named Volumes
- Managed by Docker
- More isolation
- Portable between hosts

```bash
# Create volume
docker volume create mydata

# Use volume
docker run -v mydata:/container/path
```

</div>
</div>

<!--SPEAKER-NOTE
If you want to ensure that data generated or modified inside the container persists even after the container stops running, you would opt for a volume. See Persisting container data to learn more about volumes and their use cases.

If you have specific files or directories on your host system that you want to directly share with your container, like configuration files or development code, then you would use a bind mount. It's like opening a direct portal between your host and container for sharing. Bind mounts are ideal for development environments where real-time file access and sharing between the host and container are crucial.
https://docs.docker.com/get-started/docker-concepts/running-containers/sharing-local-files/
https://docs.docker.com/get-started/docker-concepts/running-containers/persisting-container-data/
-->

---

### `--mount`

> In general, --mount is preferred. Compared to --volume, --mount flag is more explicit and supports all the available options.
>
> If you use --volume to bind-mount a file or directory that does not yet exist on the Docker host, Docker automatically creates the directory on the host for you. If you use --mount, it will error.
> https://docs.docker.com/engine/storage/bind-mounts/


Valid options for --mount type=bind include:

| Option                   | Description                                                                                  |
| ------------------------ | -------------------------------------------------------------------------------------------- |
| source, src              | The location of the file or directory on the host. This can be an absolute or relative path. |
| destination, dst, target | The path where the file or directory is mounted in the container. Must be an absolute path.  |
| readonly, ro             | If present, causes the bind mount to be mounted into the container as read-only.             |
| bind-propagation         | If present, changes the bind propagation.                                                    |

---
layout: section
---

# Intermediate concepts

---


## Multi-Stage Final Dockerfile

```dockerfile {3-5|7-9|13-15}
FROM python:3.12-slim AS builder
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --prefix=/install -r requirements.txt

FROM python:3.12-slim
COPY --from=builder /install /usr/local
COPY app.py .
CMD ["python3", "app.py"]
```

Compare the cache behavior and image size to an equivalent single-stage build.

---

## More on Mount Types

```dockerfile {5}
FROM python:3.12-slim
RUN --mount=type=tmpfs,target=/tmpdata \
    sh -c "echo 'temp' > /tmpdata/file && cat /tmpdata/file"
```

```dockerfile {4-6|7-9}
FROM alpine
RUN --mount=type=secret,id=mysecret \
    cat /run/secrets/mysecret
RUN --mount=type=ssh \
    ssh -T git@github.com || true
```

(You may not be able to try out the ssh mount in your development environment right now.)

---


## Healthchecks

Very useful feature for availability.

```dockerfile {2-4|6-7}
FROM python:3.12-slim
HEALTHCHECK CMD curl --fail http://localhost || exit 1
```

---

## Authoring Images - Metadata

```dockerfile
FROM alpine:latest

LABEL maintainer="you@example.com"
LABEL org.opencontainers.image.title="My App"
LABEL org.opencontainers.image.description="A small example application."
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.source="https://github.com/your/repo"
LABEL org.opencontainers.image.authors="Your Name <you@example.com>"

# ...
```

---

## Sharing Images (for everyone else)
*Past machine boundaries

```bash
docker login
docker push ...
docker pull ...
```

---

## Sharing Images (for us)

*Past machine boundaries

```bash
docker save myapp | gzip > myapp.tar.gz
docker load < myapp.tar.gz
docker export container_id > rootfs.tar
```


---

## ONBUILD

- Executes immediately after `FROM` in a downstream build.
- Niche but can be quite valuable


```bash
ONBUILD RUN echo foo
```

Challenge: See if you can test `ONBUILD` yourself.


---

# Common confusions, cleared up?

- What problems does cache solve? What problems does cache create?
- What did COPY vs ADD show?
- When should we mount vs copy?
- What are multi stage builds good for?
- What is a layer?
