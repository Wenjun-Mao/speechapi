# Installing `uv` inside Docker

You noticed I used `pip install uv`, but correctly noted there are other official ways to install it, like `curl` and Astral's official container image.

Here's an exact breakdown of the 3 approaches, ranking from worst to best for Docker.

## 3. The `curl | sh` method (Fastest locally, risky in Docker)
```dockerfile
# Needs curl installed
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
```
**Pros:** Downloads the pre-compiled Rust binary instantly.
**Cons:** Many minimalist Docker images (`alpine`, `distroless`, `slim`) strip `curl` and `wget` entirely to reduce security vulnerabilities. You'd have to `apt-get install curl` first, which wastes time and image size.

## 2. The `pip install uv` method (Good fallback)
```dockerfile
RUN pip install uv
```
**Pros:** Simple. It guarantees compatibility because `pip` will automatically fetch the correct python wheel (which wraps the Rust binary) for whatever OS/Architecture your Docker image is running.
**Cons:** Technically uses standard Python package resolution to install a package manager, which is a tiny bit of overhead. 

## 1. The Multi-Stage Copy (The Docker Gold Standard!)
```dockerfile
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
```
**Pros:** This is the absolute best way to do it. Astral builds an incredibly tiny Docker image containing literally nothing but the standalone compiled binaries. By using `--from=...`, Docker reaches out to GitHub Container Registry, grabs the two binary files (`uv` and `uvx`), and places them directly into your container's system `/bin/`. 
* Zero `curl` required.
* Zero `pip` overhead. 
* Instantaneous built-in caching.

> *Note: I have updated our `Dockerfile` to use this approach!*