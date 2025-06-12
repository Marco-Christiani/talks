---
theme: seriph
background: https://source.unsplash.com/collection/94734566/1920x1080
class: text-center
highlighter: shiki
lineNumbers: false
info: |
  ## Containerization
  Containerization, OCI standards, and how to use it.
drawings:
  persist: false
transition: slide-left
title: Containerization
mdc: true
addons:
  - slidev-addon-excalidraw
---

# Containerization
Understanding Containers, Images, and OCI Standards

<div class="pt-12">
  <span @click="$slidev.nav.next" class="px-2 py-1 rounded cursor-pointer" hover="bg-white bg-opacity-10">
    Press Space for next page <carbon:arrow-right class="inline"/>
  </span>
</div>

---
layout: default
---

# Table of Contents

<Toc maxDepth="2" />

---
layout: section
---

# Lesson 1: Fundamentals of Containerization

---

# What is Containerization?

- TLDR: Its like a VM but lightweight. It is sort of like a "different computer" but not as much as a VM.
- VM's run an OS with a hypervisor
- Containers use process isolation
- VM -> OS in an OS
- Container -> uses your existing OS more, only

<!-- ![[Containerization 2025-04-07 16.55.36.excalidraw]] -->

---
layout: center
---
<div class="flex flex-col items-center">

<Excalidraw
  drawFilePath="./containerization.excalidraw"
  class="w-[600px]"
  :darkMode="true"
  :background="false"
/>

</div>


---
layout: section
---

# Lesson 2: OCI Standards & Tools

---

# What is OCI?

- Open Container Initiative (OCI) tries to standardize container formats, runtimes, and distribution.
- Why should I care?
	- Concepts we discuss are basically universal
	- Hear the basic concepts and the tools make sense. Use the tools on their own and it's just esoteric magic.

## Key Specifications

1. **OCI Image Spec**: How you should bundle things up into one thing (image)
	- https://github.com/opencontainers/image-spec/
2. **OCI Runtime Spec**: How you should launch that thing and manage it.
	- https://github.com/opencontainers/runtime-spec/
3. **OCI Distribution Spec**: How you should share your images with your friends.
	- https://github.com/opencontainers/distribution-spec/

<div class="text-sm italic mt-4">
A few implementations exist but they all arrive at (for our purposes) the same product
</div>

---

# Flavors of Containerization

<div class="grid grid-cols-2 gap-4">

<div>

## Runtime Implementations
- Low level implementations of OCI Runtime Spec
- Actually launches containers
- Rarely interact with directly
- ~3 main choices, Docker's is most common

</div>

<div>

## Container Engines
- Built on runtime implementations
- Abstract away low-level details
- Manage images, running, networking
- Examples: Docker, Podman, Apptainer

</div>
</div>

```bash
# These all do basically the same thing:
docker run ubuntu
podman run ubuntu
apptainer run docker://ubuntu
```

---
layout: section
---

# Lesson 3: Images & Containers

---

# TLDR; Images vs Containers

<div class="grid grid-cols-2 gap-4">
<div>

## Images 

- Image: File -> Something you build.
	- Share it with your friends
	- Print it, frame it, gift it for Christmas
</div>
<div>

## Containers
- Container: Not a file -> A group of processes created using an image.
	- You can use the same image to start as many containers as you want
	- Cannot print it, frame it, nor share with your friends
	- Temporary
</div>
</div>

<v-click><i>Colloqially, "container" may be used as a general term, incorrectly.</i></v-click>
<br>


---

## Exercise - Image to Container

```zsh
docker pull ...
docker run ...
```

---

# Images vs Containers

<div class="grid grid-cols-2 gap-4">
<div>

## Images
- Static files you build
- Can be shared and distributed
- Reusable templates
- Stored in registries
</div>
<div>

## Containers
- Running instances of images
- Temporary and disposable
- Process groups on your system
- Cannot be shared directly
</div>
</div>

## Example - See your images and containers:
```bash
# List your images
docker image ls

# List running containers
docker container ls
```

---

# Building images and starting containers

- Build an image
```dockerfile
FROM ubuntu:latest
RUN apt update && apt install -y cowsay \
    && rm -rf /var/lib/apt/lists/*
ENTRYPOINT ["/usr/games/cowsay"]
CMD ["-e", "oo", "-TU", "Moo"]
```

```zsh
docker build -t moo:2024 .
```

- Start a container
```zsh
docker run moo:2024
```

- Check on your container
```zsh
docker container ls
# uhh, not here.. why not?
```

---

## Keep it running
Common trick for development containers:

```dockerfile
FROM ubuntu:latest
RUN apt update && apt install -y cowsay && rm -rf /var/lib/apt/lists/*
ENTRYPOINT ["/bin/bash"]
```


---

## 4. Things you will see

Some slightly less obvious tricks or patterns you might see:
- Cramming commands on one line (caching)
- Deleting things that are created as side effects, apt cache (img size)
- Building from source (clone, unzip, build, clean up)
	- Use `ADD` not `COPY`
- Setting permissions like `COPY --chmod=555 thing /thing`
- Bind mounts in builds

---

## 4. Essential Docker run flags

Just the most useful ones to know (typically abbreviated by first letter):
- Expose a port: `--port 8000:9000`
- Pass an environment variable: `--env FOO=bar`
- Mount a file/directory:
	- `--volume /path/on/host/:/path/in/container`
	- With options: `-v /thing:/thing,ro`
- Detach: `--detach`

---

## 5. The most useful CLI commands

- `build`
- `run`
- `exec -it`
- `container ls/rm/etc`
- `image ls/rm/etc`
- `volume ls/rm/etc` (maybe)

---

## 4. Persisting data

- Allow container access to a folder
- Give it a kind of virtual disk managed by docker somewhere else

```zsh
docker run -v
```

---

## 5. Docker compose

- Dockerfile: Build configuration
- Docker CLI: Run configuration
- Compose: (some) Run + (some) Build configuration

---

## 6. Bake




---
layout: section
---

# Lesson 5: Essential Docker Commands

---

# Key Dockerfile Instructions

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
Not so hard, right? IMHO 30% of the confusion about containers is actually confusion about Linux.
</div>

---

# Common Patterns

- Cramming commands on one line (caching)
- Deleting things that are created as side effects, apt cache (img size)
- Building from source (clone, unzip, build, clean up)
	- Note: `ADD` vs. `COPY`
- Setting permissions like `COPY --chmod=555 thing /thing`
- Mounts in builds
- Using build arguments
- Multi-stage builds


---

# Essential Docker Run Flags

<div class="grid grid-cols-2 gap-4">
<div>

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

</div>

<div>

## Volume Mounting
```bash
# Basic mount
docker run --volume /host:/container

# With options
docker run -v /host:/container:ro
```

## Other Common Flags
- `--detach` or `-d`: Run in background
- `--name`: Assign container name
- `--rm`: Remove after exit

</div>
</div>

---

# Most Used CLI Commands

<div class="grid grid-cols-3 gap-4">

<div>

## Container Management
- `docker run`
- `docker exec`
- `docker stop`
- `docker rm`

</div>

<div>

## Image Management
- `docker build`
- `docker pull`
- `docker push`
- `docker rmi`

</div>

<div>

## System & Info
- `docker ps`
- `docker logs`
- `docker inspect`
- `docker system prune`

</div>
</div>


---

# Data Persistence

<div class="grid grid-cols-2 gap-4">

<div>

## Bind Mounts
- Direct mapping to host filesystem
- Great for development
- Less isolation

```bash
docker run -v /host/path:/container/path
```

</div>

<div>

## Named Volumes
- Managed by Docker
- Better for production
- Portable between hosts

```bash
# Create volume
docker volume create mydata

# Use volume
docker run -v mydata:/container/path
```

</div>
</div>

---

# Docker Compose & Bake

<div class="grid grid-cols-2 gap-4">
<div>

## Docker Compose
- Dockerfile: Build configuration
- Docker CLI: Run configuration
- Compose: (some) Run + (some) Build configuration
- For multi-container applications, intuitive
- Version control your container config

```yaml
services:
  web:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - .:/workspace
      - /important/data:/important/data,ro
  db:
    image: postgres
```

</div>

<div>

## Docker Bake
- Advanced build system
- HCL or JSON configuration
- Matrix builds and targets

```hcl
target "default" {
  dockerfile = "Dockerfile"
  tags = ["myapp:latest"]
  platforms = [
    "linux/amd64",
    "linux/arm64"
  ]
}
```

</div>
</div>

---
layout: section
---

# Lesson 6: Advanced Topics

---

# Under the hood

- 2008 linux introduces cgroups
- Namespaces and unsharing

---
layout: center
class: text-center
---

# Thank You!

[Documentation](https://docs.docker.com/) · [GitHub](https://github.com/docker) · [Docker Hub](https://hub.docker.com/)

<div class="pt-12">
  <span class="px-2 py-1">
    Made with Slidev
  </span>
</div>
