import os
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
import logging

from services.asr_service import get_asr_service
from utils.downloader import download_audio_from_url

router = APIRouter(prefix="/api/v1/asr", tags=["ASR"])
logger = logging.getLogger(__name__)

class ASRRequest(BaseModel):
    url: str

class ASRResponse(BaseModel):
    text: str
    success: bool
    error: str = None

def cleanup_file(file_path: str):
    """
    Background task to remove the temporarily downloaded audio file
    after successful/failed transcription.
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Cleaned up temporary file: {file_path}")
    except Exception as e:
        logger.error(f"Failed to cleanup {file_path}: {e}")

@router.post("/transcribe", response_model=ASRResponse)
async def transcribe_audio_url(request: ASRRequest, background_tasks: BackgroundTasks):
    """
    Downloads an audio file from the provided URL, transcribes it, and responds with the text.
    """
    local_audio_path = None
    try:
        # Step 1: Download the file to a temporary location locally
        local_audio_path = await download_audio_from_url(request.url)
        
        # Ensures that no matter what, the file gets deleted after returning
        background_tasks.add_task(cleanup_file, local_audio_path)
        
        # Step 2: Acquire the preloaded FunASR logic instance and transcribe
        asr = get_asr_service()
        text = asr.transcribe(local_audio_path)
        
        # Step 3: Return response in format
        return ASRResponse(text=text, success=True)
        
    except Exception as e:
        logger.error(f"Transcription failed: {str(e)}")
        
        # If download fails before background task is added, ensure cleanup still happens
        if local_audio_path and os.path.exists(local_audio_path):
            cleanup_file(local_audio_path)
            
        raise HTTPException(status_code=500, detail=str(e))
