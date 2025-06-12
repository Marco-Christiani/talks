---
layout: section
---

# Lesson 3: Images & Containers

---

## TLDR; Images vs Containers

<div class="grid grid-cols-2 gap-4">
<div>

## Images

- Image: File -> Something you build.
	- Share it with your friends
	- Print it, frame it, gift it for Christmas
</div>
<div>

## Containers
- Container: Not a file -> A group of processes created using an image.
	- You can use the same image to start as many containers as you want
	- Cannot print it, frame it, nor share with your friends
	- Temporary
</div>
</div>

<v-click><i>Colloquially, "container" may be used as a general term, incorrectly.</i></v-click>
<br>


<!--SPEAKER-NOTE
Containers are:
1. Self-contained. Each container has everything it needs to function with no reliance on any pre-installed dependencies on the host machine.
2. Isolated. Since containers are run in isolation, they have minimal influence on the host and other containers, increasing the security of your applications.
3. Independent. Each container is independently managed. Deleting one container won't affect any others.
4. Portable. Containers can run anywhere! The container that runs on your development machine will work the same way in a data center or anywhere in the cloud!

Source: https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-a-container/
-->
---

## Exercise - Pull an image and start a container

```zsh
docker pull nginx
docker run nginx
```

---

## Images vs Containers

<div class="grid grid-cols-2 gap-4">
<div>

### Images
- Static files you build
- Can be shared and distributed
- Reusable templates
- Stored in registries
</div>
<div>

### Containers
- Running instances of images
- Temporary and disposable
- Process groups on your system
- Cannot be shared directly
</div>
</div>

### Exercise- See your images and containers
```bash
# List your images
docker image ls

# List running containers
docker container ls
```
