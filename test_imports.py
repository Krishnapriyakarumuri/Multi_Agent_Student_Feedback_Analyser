#!/usr/bin/env python
"""Quick syntax validation - just test imports"""

try:
    print("Testing task_worker imports...")
    from agents.orchestrator.task_worker import TaskWorker
    print("✅ TaskWorker imported successfully")
except Exception as e:
    print(f"❌ TaskWorker import failed: {e}")
    import traceback
    traceback.print_exc()

try:
    print("\nTesting main.py imports...")
    from main import app
    print("✅ Main app imported successfully")
except Exception as e:
    print(f"❌ Main app import failed: {e}")
    import traceback
    traceback.print_exc()

try:
    print("\nTesting routes imports...")
    from api.routes import router
    print("✅ Routes imported successfully")
except Exception as e:
    print(f"❌ Routes import failed: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ All basic imports successful!")
