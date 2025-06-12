---
layout: section
---

# More

---

## All mount types

| Type           | Description                                                                                                              |
|----------------|--------------------------------------------------------------------------------------------------------------------------|
| bind (default) | Bind-mount context directories (read-only by default)                                                                    |
| cache          | Mount a temporary directory to cache directories for compilers and package managers.                                     |
| tmpfs          | Mount a tmpfs in the build container.                                                                                    |
| secret         | Allow the build container to access secure files such as private keys without baking them into the image or build cache. |
| ssh            | Allow the build container to access SSH keys via SSH agents, with support for passphrases.                               |

https://docs.docker.com/reference/dockerfile/#run---mount

---

## COPY args

```dockerfile
FROM python:3.12-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Change the working directory to the `app` directory
WORKDIR /app

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-editable

# Copy the project into the intermediate image
ADD . /app

# Sync the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable

FROM python:3.12-slim

# Copy the environment, but not the source code
COPY --from=builder --chown=app:app /app/.venv /app/.venv

# Run the application
CMD ["/app/.venv/bin/hello"]
```

<!--NOTE: https://docs.astral.sh/uv/guides/integration/docker/#intermediate-layers-->

```dockerfile
RUN --mount=from=ghcr.io/astral-sh/uv,source=/uv,target=/bin/uv \
    uv sync
```

### COPY vs ADD
---

## Heredocs

```dockerfile
RUN <<EOF
source $HOME/.bashrc && \
echo $HOME
EOF
```

https://docs.docker.com/reference/dockerfile/#here-documents

---

## HEALTHCHECK
## ONBUILD

---

## Shell form vs exec form

---
layout: section
---

# Advanced

---
## Under the hood

- 2008 linux introduces cgroups
- Namespaces and unsharing 
