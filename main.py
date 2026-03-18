from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging

from routers.asr_router import router as asr_router
from services.asr_service import get_asr_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup behavior: Pre-load the 800M param model so we don't load it on the first request
    logger.info("Starting up API, initializing FunASR model...")
    get_asr_service()
    yield
    # Shutdown behavior
    logger.info("Shutting down API...")


app = FastAPI(
    title="SpeechAPI with FunASR",
    description="ASR endpoint for recognizing Audio URLs using Fun-ASR-Nano",
    lifespan=lifespan,
)

# Feature routing
app.include_router(asr_router)


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "SpeechAPI"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
