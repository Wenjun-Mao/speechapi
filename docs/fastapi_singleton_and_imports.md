# The Singleton Pattern & Dual Imports 

You noticed something interesting:
```python
from services.asr_service import get_asr_service
```
This exact same import statement is present in both `main.py` and `routers/asr_router.py`. To understand why, you need to understand the **Singleton Pattern**, specifically in Python Web servers.

## What is a Singleton in Python?
When an object is huge (like an 800MB Neural Network with GPU bindings), we strictly only ever want **one single copy** of it floating around our RAM during the entire life of the application. If every incoming web request instantiated `model = AutoModel(...)`, our RAM would explode instantly on the 2nd concurrent user request.

In `services/asr_service.py`, we created this:
```python
# 1. Define a global bucket but leave it empty
asr_service = None

def get_asr_service():
    global asr_service
    # 2. If the bucket is empty, fill it exactly ONCE
    if asr_service is None:
        asr_service = ASRService()
    
    # 3. Always hand back the filled bucket
    return asr_service
```
This is a basic memory cache trick (Singleton).

## Why import in main.py?
In `main.py`, our exact usage is purely to **Force the initialization early**:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # This runs when you type `uvicorn main:app`
    get_asr_service()   # <-- It's `None`, so ASRService() is instantiated and cached.
    yield
```
We don't do anything with the output here. We just call the function so the "delay" of loading the PyTorch model happens during server startup. (You see the logs trigger here).

## Why import in asr_router.py?
In `routers/asr_router.py`, your HTTP endpoint is triggered *later in time*, after a user makes a POST request to the API:

```python
@router.post("/transcribe")
async def transcribe_audio_url(...):
    # This runs when someone cURL's the API.
    # Because main.py already filled the bucket during startup,
    # this call returns instantly (<1ms).
    asr = get_asr_service()
    
    # We now possess the running instance and can safely use it.
    text = asr.transcribe(local_audio_path)
```

## Summary
By keeping the state in `services/asr_service.py`, any file across our entire project (routers, cron jobs, etc) can safely run `from services.asr_service import get_asr_service` and use `get_asr_service()`.

They don't need to know if the model is currently zero bytes or pre-loaded. The Singleton assures that whoever calls it first pays the load-time penalty (which we cleverly force `main.py` to do while booting), and anyone who calls it after gets instant access to the exact same AI pipeline.