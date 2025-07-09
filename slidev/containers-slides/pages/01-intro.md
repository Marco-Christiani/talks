---
layout: section
transition: slide-left
---

# Fundamentals of Containerization

---

## What is Containerization?

- TLDR; Its like a VM but lightweight. It is sort of like a "different computer" but not as much as a VM.
- VM's run an OS with a hypervisor
- Containers use process isolation
- VM -> OS in an OS (brings its own kernel)
- Container -> uses your existing OS more (uses your host OS kernel)

<!-- ![[Containerization 2025-04-07 16.55.36.excalidraw]] -->

---
layout: center
---

<div class="flex flex-col items-center">


<LightOrDark>
  <template #dark>
    <Excalidraw
      drawFilePath="./containerization.excalidraw"
      class="w-[600px]"
      :darkMode="true"
      :background="false"
    />
  </template>
  <template #light>
    <Excalidraw
      drawFilePath="./containerization.excalidraw"
      class="w-[600px]"
      :darkMode="false"
      :background="false"
    />
    </template>
</LightOrDark>

</div>

<TerminalToggle />

---

# Four properties of containers

Containers are...

<v-clicks>

 1. Self-contained: Has everything it needs to function.
 2. Isolated: Containers run highly contained.
 3. Independent: Containers are independently managed (similar to isolation property).
 4. Portable: Containers can run anywhere.

</v-clicks>

<br>

<v-click>
<strong>This means you can package code and ship it reliably and broadly.</strong>
</v-click>

<br>
<v-click>
Common misconception: Containers *help* with things like reproducibility but notice that is not one of the properties

https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-a-container/
</v-click>

<!--SPEAKER-NOTE
Containers are:
1. Self-contained. Each container has everything it needs to function with no reliance on any pre-installed dependencies on the host machine.
2. Isolated. Since containers are run in isolation, they have minimal influence on the host and other containers, increasing the security of your applications.
3. Independent. Each container is independently managed. Deleting one container won't affect any others.
4. Portable. Containers can run anywhere! The container that runs on your development machine will work the same way in a data center or anywhere in the cloud!

Source: https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-a-container/
-->
