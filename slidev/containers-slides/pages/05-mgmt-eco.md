---
layout: section
---

# Lesson 5: Docker Tools & Commands

---

## Essential Docker Commands

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

## Docker Compose & Bake

<div class="grid grid-cols-2 gap-4">
<div>

### Docker Compose
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

### Docker Bake
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
