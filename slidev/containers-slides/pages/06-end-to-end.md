---
layout: section
---

# Full end-to-end exercises

---

## Python with `uv`

- What follows is a series of `Dockerfile` examples that build upon each other, based on the `uv` documentation[^1].
- `uv` is a tool for managing python dependencies, packaging, and more (similar to `poetry`)
- These examples use many Docker features such as remote copy, cache mount, bind mount, multi-stage build, etc.
- **Goal:** Expose to techniques in the wild by reading real examples.
- **Task:** Discuss how each `Dockerfile` works, why decisions were made, and tradeoffs.

*The documentation suggests many examples as there is not one right answer, it depends on the use case.*

<!-- <span class="fixed bottom-2 left-2 text-xs">1: Elit Malesuada Ridiculus</span> -->

<div style="flex-grow: 1"></div>

[^1]: https://docs.astral.sh/uv/guides/integration/docker

---

## Getting `uv` - Simple approach

- We need to have `uv` installed in the image.
- Simple approach: Install it, as you would on any computer using their standard install process.

```dockerfile
FROM python:3.12-slim-bookworm

# The installer itself needs some tools like curl
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates

# Use `ADD` to copy a file from a remote source directly into our container
# What would the naive (and most common) alternative approach be for this step?
ADD https://astral.sh/uv/install.sh /uv-installer.sh

# Install uv and remove the installer (we dont ned it anymore)
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Make sure we have the installed commands in our shell `PATH`
ENV PATH="/root/.local/bin/:$PATH"
```

Source: https://docs.astral.sh/uv/guides/integration/docker/#installing-uv

---

## Getting `uv` - Using `--from`

- The `uv` project publishes images with `uv` (and `uvx`) binary
- We can directly copy the binary into our image, without using `FROM`

<v-click>

Now, the entire `Dockerfile` reduces to:

```dockerfile
FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
```

</v-click>

<v-click>

If you just need a command once during the build but not in the image you can also use a remote mount:

```dockerfile
RUN --mount=from=ghcr.io/astral-sh/uv,source=/uv,target=/bin/uv \
    uv sync
```

</v-click>

<v-click>

*Aside: the published image is a special type of image called a distroless image, basically this means we get a nice and small cache layer for fast builds and less storage.*

</v-click>

---

## Installing your project

```dockerfile
FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy in your project
COPY . /app

WORKDIR /app

# Install the project and all its dependencies
RUN uv sync --locked

# uv creates a familiar .venv/ we should add to our PATH to make commands available
ENV PATH="/app/.venv/bin:$PATH"

# Set up CMD -- This is application specific, here is an example
# (Assuming your python project provides a `myapp` command)
CMD ["myapp"]
```

---

## Cache layer optimization

> If you're using `uv` to manage your project, you can improve build times by moving your transitive dependency installation into its own layer via the --no-install options.
>
> `uv sync --no-install-project` will install the dependencies of the project but not the project itself. Since the project changes frequently, but its dependencies are generally static, this can be a big time saver. [^im_layers]


<v-click>

```dockerfile{5-9,14-16}
FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

# Copy in your project
COPY . /app

# Sync the project itself
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked
```

[^im_layers]: https://docs.astral.sh/uv/guides/integration/docker/#intermediate-layers

</v-click>


<!--pyproject.toml is required to identify the project root and name, but the project contents are not copied into the image until the final uv sync command. [^im_layers]-->


---

## Multistage - Putting it all together

```dockerfile
FROM python:3.12-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-editable

# Copy project into the intermediate image
COPY . /app

# Sync the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable

# Now, start with a clean image and only copy what we need from `builder`
FROM python:3.12-slim

# Copy the environment, but not the source code
COPY --from=builder --chown=app:app /app/.venv /app/.venv

# Run the app (depends on your application)
CMD ["/app/.venv/bin/hello"]
```


<style>
/* code { */
/*   font-size: calc(var(--slidev-code-font-size) * 0.8); */
/* } */
/* pre.slidev-code { */
/*   line-height: calc(var(--slidev-code-line-height) * 0.5) !important; */
/* } */
</style>

---

## Resources for End-to-end guides

- Docker Guides: https://docs.docker.com/guides/
