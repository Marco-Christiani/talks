# Baking data into images

## COPY

```dockerfile
# COPY <src> <dst>
COPY script.sh /usr/local/bin/script.sh
```

Copy multiple things at once:

```dockerfile
COPY script.sh fav-movies.txt todo.md /app
```

Can copy entire folders:

```dockerfile
COPY mydir/ /some/dest/
```
One of the most common examples is copying your code into the image:

```dockerfile
COPY . /app/ # recall . is your current working directory
```

---

## Controlling what is COPY'd

- You may not want to include everything in a folder...
- But you also dont want to type each file out individually...

<v-click>Use .dockerignore!</v-click>


<v-click>

Just like `.gitignore` but controls what gets included when copying data:

```
# .dockerignore
passwords.txt
secrets.json
__pycache__/
.git/
```

</v-click>

<v-click>

Now, the above files wont be included in this copy:

```dockerfile
COPY . /app/
```

</v-click>

<v-click>

You can also glob and use wildcards

```dockerfile
ADD *.png /dest/
```

</v-click>

---

## COPY flags

Set permissions when copying. Useful for making scripts executable right away.

```dockerfile
COPY --chmod=555 script.sh /usr/local/bin/script.sh
```

There is also a flag for `chown`, see if you can guess how to build an image with it.

---

## ADD

Very similar to `COPY` but you can use different sources, such as remote git repos or archives.

```dockerfile
ADD my-archive.tar.gz /app/
ADD https://example.com/config.yaml /app/config.yaml
ADD https://example.com/archive.zip /usr/src/things/
ADD git@github.com:user/repo.git /usr/src/things/
```

https://docs.docker.com/reference/dockerfile/#adding-local-tar-archives

https://docs.docker.com/reference/dockerfile/#adding-files-from-a-url

https://docs.docker.com/reference/dockerfile/#adding-files-from-a-git-repository

---

# Installing dependencies

```sh
# Create requirements for the sake of our example
echo requests > requirements.txt
echo "import requests\nprint(requests)\n" > app.py
```

```dockerfile
FROM python:3.12-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app.py .
CMD ["python3", "app.py"]
```

---

## Layers

### Cache behavior

````md magic-move {lines: true}
```dockerfile
FROM python:3.12-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app.py .
CMD ["python3", "app.py"]
```

```dockerfile
FROM python:3.12-slim
COPY app.py .
COPY requirements.txt .
RUN pip install -r requirements.txt
CMD ["python3", "app.py"]
```
````
1. With the original `Dockerfile`,

  - Make a change to app.py
  - Rebuild - What layers were cached?

2. Reorder the `COPY` line of the `Dockerfile`

  - Make a change to app.py
  - Rebuild - What layers were cached?


---

### How the layer system impacts builds

Layer caching is why you will often see commands crammed together with `&&` especially for cleanup in `RUN` commands.

Cramming commands:

```dockerfile
RUN apt update && apt install -y cowsay
```

Deleting things:

```dockerfile
RUN apt update && \
  apt install -y cowsay && \
  rm -rf /var/lib/apt/lists/* # <-- updated
```

Notice deletion occurs in the same layer

Try it out and see if you can find evidence of any difference compared to using separate `RUN` commands or not cleaning up.

---

# Aside: Copy vs Bind Mount

## COPY

```dockerfile {2-3}
FROM python:3.12-slim
COPY config.json /tmp/config.json
RUN cat /tmp/config.json
```

## Bind Mount
```dockerfile {2-3}
FROM python:3.12-slim
RUN --mount=type=bind,source=config.json,target=/tmp/config.json \
    cat /tmp/config.json
```

---

## Build Args
Pass variables at build time (not runtime):

```dockerfile
ARG VERSION=1.0
RUN echo "Version is $VERSION"
```

Build with:

```sh
docker build --build-arg VERSION=2.0 -t demo:2.0 .
```


See if you can control what base image you use (e.g., python version) using a build arg in a Dockerfile.

---
layout: section
---

# Network and Caching

---

## Controlling Network Access

```dockerfile
FROM python:3.12-slim
COPY app.py .
RUN --network=none python3 app.py || echo "Offline fetch failed"
CMD ["python3", "app.py"]
```

---

## Cache Mounts

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
ARG HTTP_PROXY # <-- build arg
ENV http_proxy=$HTTP_PROXY
RUN --mount=type=bind,source=requirements.txt,target=requirements.txt \
  pip install -r requirements.txt
```

---
layout: section
---

# Docker Compose

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

Docker Build Context: ...


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
