---
theme: seriph
# theme: neversink
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
  - tldraw
layout: cover
hideInToc: true
---


# A header

---

## Board

<tldraw class="inset-0 w-full h-full" doc="tldraw/doc-VB7EcrPHwsr6tgD6WPsJg.json"></tldraw>

---

# Welcome to your sandbox

<div class="grid grid-cols-2 gap-4">

<div>

```python {monaco-run} {autorun:false}
# file: app.py
print('Hello from the workspace!')
```

</div>


<div>

```dockerfile {monaco-run} {autorun:false}
# file: Dockerfile
FROM python:3.12-slim
COPY app.py .
CMD ["python3", "app.py"]
```
</div>
</div>

```bash {monaco-run} {autorun:false}
docker build -t myapp . && docker run myapp
```


<!-- ```bash {monaco-run} {autorun:false, height: 'auto'} -->
<!-- docker run hello-world -->
<!-- docker run hello-world -->
<!-- ``` -->
---

<RunButton cmd="docker run hello-world" />

<!-- src: pages/000-progressive-narrative.md -->

<!-- # Containerization

TLDR; Containers, Images, and being productive. -->

<!-- --- -->
<!-- hideInToc: true -->
<!-- --- -->
<!---->
<!-- # Table of Contents -->
<!---->
<!-- <Toc maxDepth="2" columns="2" /> -->
<!---->
<!-- --- -->
<!-- layout: full -->
<!-- routeAlias: terminal -->
<!-- hideInToc: true -->
<!-- transition: fade -->
<!-- --- -->
<!---->
<!-- <TerminalPanel /> -->
<!-- <TerminalToggle /> -->
<!---->
<!---->
<!-- --- -->
<!-- src: pages/01-intro.md -->
<!-- --- -->
<!---->
<!-- --- -->
<!-- src: pages/02-oci.md -->
<!-- --- -->
<!---->
<!-- --- -->
<!-- src: pages/03-img-containers.md -->
<!-- --- -->
<!---->
<!-- --- -->
<!-- src: pages/03-1-building.md -->
<!-- --- -->
<!---->
<!-- --- -->
<!-- src: pages/04-flags-mounts.md -->
<!-- --- -->
<!---->
<!-- --- -->
<!-- src: pages/05-mgmt-eco.md -->
<!-- --- -->
<!---->
<!-- --- -->
<!-- src: pages/06-end-to-end.md -->
<!-- --- -->
<!---->
<!-- --- -->
<!-- src: pages/07-advanced.md -->
<!-- --- -->
<!---->
<!-- --- -->
<!-- layout: center -->
<!-- class: text-center -->
<!-- --- -->
<!---->
<!-- # References -->
<!---->
<!-- [Documentation](https://docs.docker.com/) · [GitHub](https://github.com/docker) · [Docker Hub](https://hub.docker.com/) -->
<!---->
<!-- <div class="pt-12"> -->
<!--   <span class="px-2 py-1"> -->
<!--     Made with Slidev -->
<!--   </span> -->
<!-- </div> -->
