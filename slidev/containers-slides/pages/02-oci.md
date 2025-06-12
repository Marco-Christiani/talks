---
layout: section
transition: slide-left
---

# Lesson 2: OCI Standards & Tools

---

## What is OCI?

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

## Flavors of Containerization

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