# FastAPI `Depends()` & Dependency Injection

You asked how FastAPI's `Depends()` feature would fit into our project instead of our current Singleton approach, and why people use it.

## 1. What is Dependency Injection (DI)?
Dependency Injection is a scary string of words for a very simple concept: 
*"Instead of a function going out and fetching the tools it needs, we simply pass the tools into the function as arguments."*

In FastAPI, this is done using the `Depends()` keyword. It tells FastAPI to compute or retrieve something *before* the router executes, and then give the result to the router.

## 2. How it would look in our project
If we rewrote our app to use FastAPIs built-in DI and lifespan states, it would look like this:

**In `main.py`:**
```python
from fastapi import FastAPI, Request
from services.asr_service import ASRService

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the model and attach it to the raw FastAPI "state" dictionary
    app.state.asr_model = ASRService()
    yield
    # Clean it up when stopping
    app.state.asr_model = None

app = FastAPI(lifespan=lifespan)
```

**In a new file `dependencies.py`:**
We create a function whose sole job is to reach into the request and pull out the model.
```python
from fastapi import Request

async def get_asr_dependency(request: Request):
    # Reach into the app state to grab what Lifespan created
    return request.app.state.asr_model
```

**In `routers/asr_router.py`:**
Notice how we add it as an argument using `Depends()`.
```python
from fastapi import APIRouter, Depends
from dependencies import get_asr_dependency

router = APIRouter()

@router.post("/transcribe")
async def transcribe_audio_url(
    request: ASRRequest, 
    asr_service = Depends(get_asr_dependency) # <--- The Magic happens here
):
    # We no longer "import" the service, FastAPI hands it to us!
    text = asr_service.transcribe("some/audio/path.mp3")
    return {"text": text}
```

## 3. Pros and Cons of Depends() vs Singleton

### Why the `Depends()` approach is heavily loved (Pros):
1. **Pristine Unit Testing:** If you write a test for `/transcribe`, you don't want to actually boot an 800MB model into your GPU. With `Depends()`, FastAPI allows you to do `app.dependency_overrides[get_asr_dependency] = MockFakeAIModel`. It seamlessly injects a fake object, making testing effortless. Testing Singletons is significantly more annoying and requires mocking the `sys.modules` monkey-patching.
2. **Explicit Signatures:** By looking at the `def transcribe_audio_url(...)` arguments, a developer instantly knows exactly what this function relies on to survive without having to read its internal code.
3. **Database Scoping:** `Depends()` yields exactly when a request starts, and finishes exactly when a request ends. This makes it the undisputed king for Database connect-and-disconnect sessions.

### Why we used the Singleton approach instead (Cons of Depends):
1. **Boilerplate overhead:** As you can see above, to use DI for a machine learning model, we had to attach it to the raw dictionaries inside `app.state`, then write a dependency getter, and then pass it as an argument.
2. **Outside the Web Scope:** What if you later add a background `celery` worker or a local CLI terminal command that *also* needs `ASRService`? Using the `app.state` method means `ASRService` is trapped inside the FastAPI web server. A background script has no `Request` object, so it can't use `Depends()`. 

The Singleton (our current approach) allows *any* file—web request or otherwise—to just `from asr_service import get_asr_service` and use it immediately without needing to know about HTTP Requests.