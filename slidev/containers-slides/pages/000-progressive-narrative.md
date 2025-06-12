---
layout: section
---

# Do it yourself

---
layout: section
---

# Part 1: Boilerplate

---

## Starting point

```dockerfile
# hello.Dockerfile
FROM python:3.12-slim
CMD ["python3", "-c", "print('Hello, Docker')"]
```

## Try It

```bash
docker build -t hello-docker -f hello.Dockerfile .
docker run hello-docker
```

---
layout: section
---

# Part 2: Running Code with Args

---
layout: two-cols
---

# ENTRYPOINT

```dockerfile {3}
FROM python:3.12-slim
COPY app.py .
ENTRYPOINT ["python3", "app.py"]
```

TODO: Explain entrypoint

::right::

# CMD

```dockerfile {3}
FROM python:3.12-slim
COPY app.py .
ENTRYPOINT ["python3", "app.py"]
CMD ["https://httpbin.org/json"]
```

TODO: explain the cmd

---

# Part 3: Installing Python Deps

## Installing `requests`

```dockerfile {4|5}
FROM python:3.12-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app.py .
CMD ["python3", "app.py"]
```

---
layout: section
---

# Part 4: Copy vs Mount

---

## COPY

```dockerfile [COPY] {2-3}
FROM python:3.12-slim
COPY config.json /tmp/config.json
RUN cat /tmp/config.json
```

---

## Build context, .dockerignore

TODO

---

## Bind Mount
```dockerfile [Bind mount] {2-3}
FROM python:3.12-slim
RUN --mount=type=bind,source=config.json,target=/tmp/config.json \
    cat /tmp/config.json
```

---
layout: section
---

# Part 5: Network and Caching

---

## Controlling Network Access

```dockerfile
FROM python:3.12-slim
COPY app.py .
RUN --network=none python3 app.py || echo "Offline fetch failed"
CMD ["python3", "app.py"]
```

---

## Caching Dependencies

```dockerfile
FROM python:3.12-slim
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt
COPY app.py .
CMD ["python3", "app.py"]
```

---

## Proxy

Bake the value into the image so you dont have to set it at runtime

```dockerfile {2-3}
FROM python:3.12-slim
ARG HTTP_PROXY
ENV http_proxy=$HTTP_PROXY
RUN --mount=type=bind,source=requirements.txt,target=requirements.txt \
  pip install -r requirements.txt
```

---
layout: section
---

# Part 8: Compose

---

## Intro to Docker Compose

````md magic-move {lines: true}
```sh
# Without compose:
docker run --rm \
  -e http_proxy=https://... \
  -v "$(pwd):/app" \
  -w /app \
  alpine:latest \
  python3 app.py
```

```sh
# With compose:
docker compose up
```
```yaml {*|1-2|3|4|5|6-7|8-9|10|*}
# .
# |- compose.yml
services:
  app:
    build: alpine:latest
    environment:
      - http_proxy=https://...
    volumes:
      - .:/app
    command: ["python3", "app.py"]
```

```yaml {1-3,6-7}
# .
# |- compose.yml
# |- Dockerfile
services:
  app:
    build:
      context: .
    environment:
      - http_proxy=https://...
    volumes:
      - .:/app
    command: ["python3", "app.py"]
```
````

---

## Compose build context, multiple build files

````md magic-move {lines: true}
```yaml
# .
# |- docker/
# | |- compose.yml
# | |- Dockerfile
services:
  app:
    build:
      context: ..
```

```yaml
# .
# |- docker/
# | |- compose.yml
# | |- Dockerfile
# | |- Dockerfile.server
services:
  app:
    build:
      context: ..
  server:
    build:
      context: ..
      dockerfile: Dockerfile.server
```
````

---

## Compose RHEL/PME, additional contexts, secrets

### Using additional contexts

```yaml
# compose.yml
services:
  app:
    build:
      context: .
      additional_contexts:
        # "repos" is the name of the context
        repos: /etc/yum.repos.d
```


```dockerfile
# Dockerfile
FROM registry.access.redhat.com/ubi9/ubi

# Copy in host repo definitions using the "repos" context (rather than the default ..)
COPY --from=repos /etc/yum.repos.d /etc/yum.repos.d
RUN dnf install -y emacs && \
    dnf clean all
```

---

## Compose: RHEL/PME, additional contexts, secrets

### Using a secret

```yaml
# compose.yaml
services:
  app:
    build:
      context: .
      secrets:
        - repos

secrets:
  repos:
    file: /etc/yum.repos.d
```

```dockerfile
# Dockerfile
FROM registry.access.redhat.com/ubi9/ubi

RUN --mount=type=secret,id=repos,target=/etc/yum.repos.d \
    dnf install -y emacs && \
    dnf clean all
```

---


## Bake

```hcl
group "default" {
  targets = ["app"]
}

target "app" {
  dockerfile = "Dockerfile"
  tags = ["myapp:latest"]
  platforms = ["linux/amd64", "linux/arm64"]
  context = "."
}
```

TODO: explain and have a run command

---
layout: section
---

# Part 8: Intermediate concepts

---

## Multi-Stage Final Dockerfile

```dockerfile {3-5|7-9|13-15}
# syntax=docker/dockerfile:1.4
FROM python:3.12-slim AS builder
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --prefix=/install -r requirements.txt

FROM python:3.12-slim
COPY --from=builder /install /usr/local
COPY app.py .
CMD ["python3", "app.py"]
```

---

## More on Mount Types

```dockerfile {5}
# syntax=docker/dockerfile:1.4
FROM python:3.12-slim
RUN --mount=type=tmpfs,target=/tmpdata \
    sh -c "echo 'temp' > /tmpdata/file && cat /tmpdata/file"
```

```dockerfile {4-6|7-9}
# syntax=docker/dockerfile:1.4
FROM alpine
RUN --mount=type=secret,id=mysecret \
    cat /run/secrets/mysecret
RUN --mount=type=ssh \
    ssh -T git@github.com || true
```

---


## Build checks and Healthchecks

```dockerfile {2-4|6-7}
FROM python:3.12-slim
HEALTHCHECK CMD curl --fail http://localhost || exit 1
ONBUILD COPY . /app
ONBUILD RUN pip install -r /app/requirements.txt
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

# Recap

- What problems does cache solve?
- What did COPY vs ADD show?
- When should we mount vs copy?
- What are multi stage builds good for?
- What is a layer?

---
layout: center
class: text-center
---

# Questions?
### Lets build something together


