# SpeechAPI - FunASR Nano

A robust FastAPI web service for performing Automatic Speech Recognition (ASR) on audio URLs using the state-of-the-art **FunASR-Nano-2512** model.

## Features
- **URL Streaming**: Submit an Audio URL, and the server temporarily safely downloads and transcribes it.
- **FastAPI Modular Structure**: Clean architectural separation using `APIRouter`, services, and dependencies.
- **Singleton Model Caching**: Eliminates per-request load times by pinning the 800MB Neural Network intelligently using FastAPI `Lifespan`.
- **Docker Ready**: Easy containerized deployments with or without Nvidia GPU support.

## Local Setup

### Prerequisites
- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (The lightning-fast python package manager)
- FFmpeg (for audio processing)
  - Ubuntu/Debian: `sudo apt install ffmpeg`

### Installation
1. Clone this repository
2. Sync the dependencies and initialize the virtual environment:
   ```bash
   uv sync
   ```
3. Start the server (this will download the model automatically on first startup):
   ```bash
   uv run uvicorn main:app --host 0.0.0.0 --port 8000
   ```

---

## Docker Deployment (Recommended)

Docker is the easiest way to run the API, as it completely isolates Python environments and the necessary C++ formatting dependencies (like `editdistance` and `ffmpeg`).

1. Build & Run in the background:
   ```bash
   docker compose up -d --build
   ```
2. For **GPU capabilities**:
   If your server has Nvidia Container Toolkit set up, uncomment the `deploy` block inside `compose.yaml` to pass the GPUs securely to the container!

3. To view the logs (especially during the first model download run):
   ```bash
   docker compose logs -f
   ```

---

## API Usage

Once the server is running (either locally or via Docker), navigate to the interactive Swagger UI:  
**Docs URL:** http://localhost:8000/docs

### 1. Transcribe Audio URL
**Endpoint:** `POST /api/v1/asr/transcribe`

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/asr/transcribe" \
     -H "Content-Type: application/json" \
     -d '{
           "url": "https://example.com/some_audio_file.mp3"
         }'
```

**Expected Response (JSON):**
```json
{
  "text": "这是一段测试音频的文字返回。",
  "success": true,
  "error": null
}
```

### 2. Health Check
**Endpoint:** `GET /health`
```bash
curl "http://localhost:8000/health"
```
