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

# When building dist/assets/monaco is 7.5M
# The largest file is dist/assets/monaco/bundled-types-DA6aMCyR.js is 2MB
# Also, I see languages being bundles that I clearly do not use
#  e.g., dist/assets/monaco/php-CpIb_Oan.js while those js files are small
#  there is a file for seemingly every language monaco supports and it points
#  to a problem with monaco bundling.
#
# From the docs:
# "You can optionally switch to load types from CDN by setting the following headmatter
# This feature is powered by @typescript/ata and runs completely on the client-side."
# https://sli.dev/custom/config-monaco#auto-type-acquisition
#
# However, this seems to make no difference.
# monacoTypesSource: ata
---


# Containerization

TLDR; Containers, Images, and being productive.

---
hideInToc: true
---

# Table of Contents

<Toc maxDepth="1" columns="2" />

---
src: pages/01-intro.md
---

---
src: pages/02-oci.md
---

---
src: pages/03-0-img-containers.md
---

---
src: pages/03-1-building.md
---

---
src: pages/03-2-flags-mounts.md
---

---
src: pages/04-0-building.md
---

---
src: pages/04-1-intermediate.md
---

---
src: pages/05-mgmt-eco.md
---

---
src: pages/06-end-to-end.md
---

---
src: pages/07-advanced.md
---

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

---

# Board

<tldraw class="inset-0 w-full h-full" doc="tldraw/doc-Gan_pT8nhnkhJSrLPb8V8.json"></tldraw>

<!--
Switch to this slide when i need to draw things
-->

---

# Sandbox demo

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
---

# Run demo

<RunButton cmd="docker run hello-world" />
