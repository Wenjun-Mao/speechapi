import os
import time
import torch
import logging
import statistics

os.environ["MODELSCOPE_CACHE"] = "./models"
from funasr import AutoModel

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

NUM_RUNS = 50

def run_test_loop(model, test_files, mode_name):
    print(f"\n\n" + "="*50)
    print(f"=== {mode_name} MODE ({NUM_RUNS} runs) ===")
    
    # Warmup
    if os.path.exists(test_files[0]):
        print(f"Running warmup for {mode_name}...")
        t0 = time.time()
        model.generate(input=[test_files[0]], cache={}, batch_size=1, language="中文", itn=True)
        t1 = time.time()
        print(f"🟠 Warmup took {t1 - t0:.3f} seconds")
        
    results = {f: [] for f in test_files if os.path.exists(f)}
    
    for i in range(NUM_RUNS):
        print(f"\n--- Run {i+1}/{NUM_RUNS} ---")
        for f in test_files:
            if os.path.exists(f):
                t0 = time.time()
                res = model.generate(input=[f], cache={}, batch_size=1, language="中文", itn=True)
                t1 = time.time()
                duration = t1 - t0
                results[f].append(duration)
                print(f"[{mode_name}] {f}: {duration:.3f} seconds")
                
    print(f"\n=== {mode_name} STATS ===")
    for f, times in results.items():
        mean = statistics.mean(times)
        stdev = statistics.stdev(times) if len(times) > 1 else 0.0
        print(f"File: {f}")
        print(f"  Mean   : {mean:.3f} s")
        print(f"  StdDev : {stdev:.3f} s")
        print(f"  Min/Max: {min(times):.3f} s / {max(times):.3f} s")
        
    return results


def run_benchmark():
    model_dir = "FunAudioLLM/Fun-ASR-Nano-2512"
    logger.info(f"Initializing standard AutoModel on device: {'cuda:0' if torch.cuda.is_available() else 'cpu'}...")
    
    # Load model once
    model = AutoModel(
        model=model_dir,
        device="cuda:0" if torch.cuda.is_available() else "cpu",
        disable_update=True,
        trust_remote_code=True,
        remote_code="./funasr_custom_arch/model.py",
    )
    
    test_files = ["data/1.mp3", "data/2.wav"]
    
    # Verify files exist
    for f in test_files:
        if not os.path.exists(f):
            logger.warning(f"File {f} not found. Some tests will be skipped.")

    # 1. TEST STANDARD MODE
    standard_results = run_test_loop(model, test_files, "STANDARD")

    # 2. APPLY JIT COMPILE
    print("\n\n" + "="*50)
    print("=== APPLYING torch.compile(dynamic=True) ===")
    try:
        model.model = torch.compile(model.model, dynamic=True)
        print("Compilation applied.")
    except Exception as e:
        print(f"Failed to apply torch.compile: {e}")
        return

    # 3. TEST COMPILED MODE
    compiled_results = run_test_loop(model, test_files, "COMPILED")
    
    # 4. FINAL COMPARISON
    print("\n\n" + "="*50)
    print("=== FINAL COMPARISON (Mean Latency) ===")
    for f in test_files:
        if os.path.exists(f):
            std_mean = statistics.mean(standard_results[f])
            comp_mean = statistics.mean(compiled_results[f])
            diff_percent = ((std_mean - comp_mean) / std_mean) * 100
            print(f"File: {f}")
            print(f"  Standard : {std_mean:.3f} s")
            print(f"  Compiled : {comp_mean:.3f} s")
            if diff_percent > 0:
                print(f"  Result   : COMPILED IS FASTER by {diff_percent:.1f}% 🚀")
            else:
                print(f"  Result   : Standard is faster by {abs(diff_percent):.1f}% 📉")

if __name__ == "__main__":
    run_benchmark()
