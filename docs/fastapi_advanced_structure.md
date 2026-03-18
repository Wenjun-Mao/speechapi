# Modular FastAPI Structure and Lifespan

When you're building a larger FastAPI application, throwing all your routes, setup magic, and model processing logic into `main.py` creates a "God File." It becomes 1,000 lines long, terribly hard to debug, and merges vastly different concerns. 

This project was intentionally decoupled into multiple layers right from the start to show how standard production-ready APIs are built.

## 1. APIRouter: The "Mini FastAPI"
If `FastAPI` instance is the main switchboard of an application, `APIRouter` acts like local mini-switchboards per feature. Instead of creating everything via `@app.get(...)` inside `main.py`, you define a `router = APIRouter(...)` inside a self-contained feature file (like `asr_router.py`). 

By putting endpoints in the router, the logic is totally isolated. Then at the very end in `main.py`, you "plug in" that router using:
```python
app.include_router(asr_router)
```
This makes it dead simple to add \`/api/v1/auth\` or \`/api/v1/billing\` later simply by creating a new `SomethingRouter.py` file!

## 2. Lifespan: Safe & Predictable Server State

For years, FastAPI developers used `@app.on_event("startup")` and `@app.on_event("shutdown")`. However, they had a major problem: if the startup event succeeded but some other part of the app crashed, the shutdown events sometimes never fired, leaving resources (like expensive ML GPU caches or Database Connections) stranded.

Enter `asynccontextmanager`. A Lifespan is a single function that yields control backwards to FastAPI:
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- 1. Code here runs BEFORE the API accepts requests ---
    print("Loading AI Model before Traffic hits...")
    get_asr_service()

    yield # <--- 2. Server pauses here and accepts HTTP traffic

    # --- 3. Code here runs AFTER the API shuts down ---
    print("Graceful shutdown: wiping cache, releasing GPU")
```

Why does this matter for AI models? Because our Fun-ASR Nano model is ~800 Megabytes and uses CUDA/CPU Memory. If we loaded the model inside the transcription endpoint (`/transcribe`), the very first user who calls the API would be stuck waiting 10-15 seconds for their response because the model has to load first. 

Instead, placing it before the `yield` ensures the application is completely ready and fully pre-loaded **before** it even says "Hello, I am listening on port 8000!".

## 3. The Services/Utils Pattern

- **`services/`**: Code that actually does the domain business logic. (e.g., A module that manages the ASR models, inference configurations, and error masking).
- **`routers/`**: Code that purely handles *HTTP lifecycle*. (e.g., Receiving `url` from JSON, throwing HTTP 400 Exceptions, handling BackgroundTasks.)
- **`utils/`**: Dumb helper scripts that don't know anything about FastAPI *or* your specific AI Model. They just do things like downloading files to disk.

By having routers talk to services, you separate "Web Request stuff" from "AI execution stuff".