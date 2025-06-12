---
layout: section
---

# Lesson 4: Essential Docker Commands

---

## Essential Docker run flags
<!--Runtime configuration-->

Just the most useful ones to know (typically abbreviated by first letter):
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
docker run -it ubuntu
```

## Port Mapping

```bash
docker run --port 8000:9000
# or
docker run -p 8000:9000
```

## Environment Variables

```bash
docker run --env FOO=bar
# or
docker run -e FOO=bar
```

## Detach

```bash
docker run nginx # starts in foreground
docker run -d nginx # starts in background, prints container id

# Use the Docker CLI to see if its running and check the logs
docker container ls # you can see how --name is useful
docker logs container_name_or_id # Check output
docker logs -f container_name_or_id # Follow output
```

---

## Persisting data

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

Source: https://docs.docker.com/engine/storage/bind-mounts/
> In general, --mount is preferred. Compared to --volume, --mount flag is more explicit and supports all the available options.
>
> If you use --volume to bind-mount a file or directory that does not yet exist on the Docker host, Docker automatically creates the directory on the host for you. If you use --mount, it will error.


Valid options for --mount type=bind include:

| Option                   | Description                                                                                  |
| ------------------------ | -------------------------------------------------------------------------------------------- |
| source, src              | The location of the file or directory on the host. This can be an absolute or relative path. |
| destination, dst, target | The path where the file or directory is mounted in the container. Must be an absolute path.  |
| readonly, ro             | If present, causes the bind mount to be mounted into the container as read-only.             |
| bind-propagation         | If present, changes the bind propagation.                                                    |
