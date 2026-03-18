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

# Copy the dependency files
# We do this before copying the code to maximize Docker layer caching
COPY pyproject.toml uv.lock ./

# Sync the dependencies
# using --frozen ensures we lock to exactly what's tested in uv.lock
# using --no-dev excludes any dev packages if they existed
RUN uv sync --frozen --no-dev

# Now copy the rest of your application code
COPY . .

# Ensure the models and data directories exist
RUN mkdir -p models data

# Expose the API port
EXPOSE 8000

# Run the app exactly how we do locally using uv
# Uvicorn bound to 0.0.0.0 is necessary for Docker container networking
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
