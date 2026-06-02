import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from search_engine import run_search

def test_logger(src, msg, lvl="info"):
    print(f"[{src.upper()}] {msg}")

print("Testing LinkedIn Only Orchestrator...")
run_search(["Security Engineer"], "week", log_cb=test_logger)
print("Finished!")
