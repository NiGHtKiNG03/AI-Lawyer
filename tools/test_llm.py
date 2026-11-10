"""Quick check that your key, provider and model work.  Run from the project folder:  python tools/test_llm.py"""
import sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from lawyer import llm

t = time.time()
try:
    print(llm.complete("Reply briefly.", [{"role": "user", "content": "Say hello in one word."}]))
except Exception as e:  # noqa: BLE001
    print("ERROR:", e)
print(round(time.time() - t, 1), "seconds")
