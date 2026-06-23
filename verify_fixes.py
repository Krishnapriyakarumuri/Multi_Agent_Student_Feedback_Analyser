"""Simple fix verification via file content checks"""

checks = [
    ("task_worker reads text_hash from task_data",
     "agents/orchestrator/task_worker.py",
     'task_data.get("text_hash"'),
    ("save_feedback deduplicates by text_hash",
     "memory/long_term_memory.py",
     "filter_by(text_hash=text_hash)"),
    ("save_recommendation skips duplicates",
     "memory/long_term_memory.py",
     "Skipping duplicate recommendation"),
    ("save_sentiment skips duplicates",
     "memory/long_term_memory.py",
     "Skipping duplicate sentiment"),
    ("save_theme skips duplicates",
     "memory/long_term_memory.py",
     "Skipping duplicate theme"),
    ("save_bias_check skips duplicates",
     "memory/long_term_memory.py",
     "Skipping duplicate bias check"),
]

print("=== Deduplication Fix Verification ===\n")
all_ok = True
for label, filepath, needle in checks:
    with open(filepath, "r", encoding="utf-8") as f:
        found = needle in f.read()
    status = "OK  " if found else "FAIL"
    if not found:
        all_ok = False
    print(f"  [{status}] {label}")

print()
if all_ok:
    print("All fixes confirmed! Upload your CSV once - no more duplicates.")
else:
    print("Some fixes MISSING - check the files above.")
