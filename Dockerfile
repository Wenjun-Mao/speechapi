FROM python:3.13-slim

# Install system dependencies required for compiling some packages (like editdistance) and handling audio
RUN apt-get update && apt-get install -y \
    build-essential \
    ffmpeg \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# The "Gold Standard" way to install uv in Docker using multi-stage builds
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set uv configuration for Docker compilation
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Copy the dependency files
# We do this before copying the code to maximize Docker layer caching
COPY pyproject.toml uv.lock ./

# Sync the dependencies using a BuildKit cache mount
# This stops uv from redownloading packages between docker builds!
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Now copy the rest of your application code
COPY . .

# Run sync again to install the project itself (if applicable)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Ensure the models and data directories exist
RUN mkdir -p models data

# Expose the API port
EXPOSE 8000

# Run the app exactly how we do locally using uv
# Uvicorn bound to 0.0.0.0 is necessary for Docker container networking
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
