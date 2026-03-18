# Python Module Scope & The `global` Keyword

To understand why `main.py` does not need to declare `asr_service = None`, you need to understand how Python handles "Modules", "Namespaces", and the `global` keyword.

## 1. Modules are their own isolated rooms
Every `.py` file in Python is a **Module**. When you write variables or functions at the "top level" of a file (like we did in `asr_service.py`), they belong *exclusively* to that file's namespace. 

In `services/asr_service.py`, we wrote:
```python
asr_service = None  # This lives in the "asr_service" namespace

def get_asr_service():
    global asr_service
    if asr_service is None:
        asr_service = ASRService()
    return asr_service
```

When Python sees the word `global` inside a function, it translates to: *"Look for a variable defined at the top-level **of the file where this function is written**."* 

It **does not** mean "look across the entire program." Python's `global` really just means "Module-level".

## 2. When `main.py` imports...
In `main.py`, you wrote:
```python
from services.asr_service import get_asr_service
```
This tells Python: "Give me the `get_asr_service` function from the `asr_service` module."

When `main.py` actually *executes* `get_asr_service()`, the code inside that function runs. When it hits the `global asr_service` line, the function remembers where it was born! It looks at exactly *its own native file* (`asr_service.py`) for the `asr_service` variable. 

It completely ignores `main.py`'s variables. Therefore, `main.py` doesn't need an `asr_service = None` bucket of its own. It's using the bucket stored inside `asr_service.py`.

## 3. The `sys.modules` Cache (The Real Magic)
"But what if we import it in 10 different files? Don't we get 10 different buckets?"
No! 

When Python imports a file for the very first time, it executes it from top to bottom, and saves the resulting module into a hyper-fast hidden dictionary called `sys.modules`. 
If `routers/asr_router.py` later tries to import `asr_service.py` again, Python says: "Wait, I already built this module earlier!" and hands over the *exact same cached bucket*. 

This is why the Singleton pattern works seamlessly in Python without extra tools. The module itself acts as a naturally shared global box.