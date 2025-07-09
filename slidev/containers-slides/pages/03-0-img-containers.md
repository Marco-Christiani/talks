---
layout: section
---

# Images & Containers

---

# TLDR; Images vs Containers

<div class="grid grid-cols-2 gap-4">

<div>
<v-click>

## Images

- Image: File -> Something you build.
	- Share it with your friends
	- Print it, frame it, gift it for Christmas
</v-click>
</div>

<div>

<v-click>

## Containers

- Container: Not a file -> A group of processes created using an image.
	- You can use the same image to start as many containers as you want
	- Cannot print it, frame it, nor share with your friends
	- Temporary
</v-click>

</div>

</div>


<v-click><i>Colloquially, "container" may be used as a general term, incorrectly.</i></v-click>
<br>


---

## Exercise - Pull an image and start a container

```bash
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

<v-click>

### Exercise- See your images and containers
```bash
# List your images
docker image ls

# List running containers
docker container ls
```

</v-click>
