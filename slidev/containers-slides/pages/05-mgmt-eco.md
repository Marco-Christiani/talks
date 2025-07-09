---
layout: section
---


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
- HCL or JSON configs
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
