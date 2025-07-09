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

## Heredocs

- Super useful for shell scripting in general, not just Docker (i.e. `bash`, `zsh`)
- TLDR: It lets you inline a file.

Basic syntax:

```sh
cat <<delimiter
  Body of the here doc
  can be many lines...
delimiter
```

- Where `delimiter` can be basically anything with common choice being `EOF` for "end of file" or sometimes `!` because its easy to type.
- `cat` is just an example command that can do something with `stdin` which is where the body of the here-document is sent
- You could use other commands that know how to process `stdin`

---

## Heredocs: Example

Often used to create files like:

Basic syntax (type this in your shell right now):

```sh
cat <<EOF > example.sh
echo "running ls"
ls
echo "done"
EOF
```

Now, check the contents of `example.sh`

```sh
cat example.sh
```

For more details on syntax and what here-documents can do see https://pubs.opengroup.org/onlinepubs/9699919799/utilities/V3_chap02.html#tag_18_07_04

---

## Heredocs in Docker: `COPY`

- Supported for some commands (`COPY`, `RUN`)
- Saves you from maintaining separate files which can increase maintenance burden and complexity

Inline a file so you dont need to make a separate file and copy it in:

```dockerfile
COPY <<EOF example.txt
This is a really important file to have.
It spans a few lines,
but is quite short...
So I decided to inline it with a heredoc
EOF
```

---

## Heredocs in Docker: `RUN`

Use it to run a multi-line command without escaping every newline:

```dockerfile
RUN <<EOF
source $HOME/.bashrc
echo $HOME
EOF
```

Even supports shebang headers:

```dockerfile
RUN <<EOF
#!/usr/bin/env python
print("hello world")
EOF
```

https://docs.docker.com/reference/dockerfile/#here-documents

---

## Heredocs in Docker: inline builds

My favorite fun-fact/feature for quickly building images!

```sh
docker build -t heredoc-build-example -<<!
FROM alpine:latest
# ...
CMD ["/bin/sh"]
!
```

---

## Inspecting images


```dockerfile
docker history docker-demo
```

```dockerfile
docker inspect docker-demo
```

---

## Shell form vs exec form

---
layout: section
---

# Advanced

---

## Bake

TODO

```hcl
group "default" {
  targets = ["app"]
}

target "app" {
  dockerfile = "Dockerfile"
  tags = ["myapp:latest"]
  platforms = ["linux/amd64", "linux/arm64"]
  context = "."
}
```

<!-- explain and have a run command -->

---

## Under the hood

- 2008 linux introduces cgroups
- Namespaces and unsharing
- ...
