import os
import uuid
import httpx
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError)),
    before_sleep=lambda retry_state: logger.warning(
        f"Download failed, retrying ({retry_state.attempt_number}/3)... "
        f"Exception: {retry_state.outcome.exception()}"
    )
)
async def download_audio_from_url(url: str, output_dir: str = "./data") -> str:
    """
    Downloads an audio file from a URL to a local temporary path.
    Retries up to 3 times on network or HTTP errors.
    """
    os.makedirs(output_dir, exist_ok=True)

    # Try to extract a reasonable extension for caching safety
    file_ext = url.split("?")[0].split(".")[-1]
    if not file_ext or len(file_ext) > 4:
        file_ext = "tmp"

    file_path = os.path.join(output_dir, f"{uuid.uuid4().hex}.{file_ext}")

    logger.info(f"Downloading audio from {url} to {file_path}")
    async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
        response = await client.get(url)
        response.raise_for_status()
        with open(file_path, "wb") as f:
            f.write(response.content)

    return file_path
