import os
import logging
import torch

logger = logging.getLogger(__name__)


class ASRService:
    def __init__(self):
        # Ensure model cache points to our local repo model storage
        os.environ["MODELSCOPE_CACHE"] = "./models"

        # Load custom architecture and tokenizer dependencies
        from funasr import AutoModel

        model_dir = "FunAudioLLM/Fun-ASR-Nano-2512"
        logger.info(f"Initializing FunASR AutoModel from {model_dir}...")

        self.model = AutoModel(
            model=model_dir,
            device="cuda:0" if torch.cuda.is_available() else "cpu",
            disable_update=True,
            trust_remote_code=True,
            remote_code="./funasr_custom_arch/model.py",
        )
        logger.info("AutoModel initialized successfully.")

    def transcribe(self, audio_path: str) -> str:
        """
        Transcribe an audio file using the Nano model.
        """
        res = self.model.generate(
            input=[audio_path], cache={}, batch_size=1, language="中文", itn=True
        )

        if isinstance(res, list) and len(res) > 0 and "text" in res[0]:
            return res[0]["text"]
        return ""


# Singleton to avoid reloading the huge model on every request
asr_service = None


def get_asr_service():
    global asr_service
    if asr_service is None:
        asr_service = ASRService()
    return asr_service
