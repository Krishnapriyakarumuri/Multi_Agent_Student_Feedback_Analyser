# 🚀 Quick Start - Monitoring Your Fixed Pipeline

## What Was Wrong
- Preprocessing completed ✅
- Other agents were stuck in queue ❌
- **No background worker** to process the queued tasks

## What I Fixed
- Created `TaskWorker` that runs in background
- Automatically processes tasks from each agent's queue
- Moves tasks through the pipeline: preprocessing → embedding → sentiment → theme → bias → recommendation

## How To See It Working

### 1. Start Server
```bash
python main.py
```
Look for:
```
⚡ Background Task Worker started - Processing agent pipeline...
👂 Listening for preprocessing agent tasks...
👂 Listening for embedding agent tasks...
[etc...]
```

### 2. Upload CSV via Frontend
```bash
streamlit run frontend/app.py
```
Then upload a CSV file

### 3. Watch the Magic ✨

**New Diagnostic Endpoint:**
```bash
# In another terminal:
curl http://localhost:8000/api/v1/worker/status | python -m json.tool
```

Output:
```json
{
  "queue_depths": {
    "preprocessing": 0,
    "embedding": 5,    ← Tasks waiting
    "sentiment": 3,    ← Tasks waiting
    "theme": 0,
    "bias": 0,
    "recommendation": 0
  },
  "total_tasks_in_pipeline": 8
}
```

As you repeat this command, you'll see:
- preprocessing queue → 0 (done)
- embedding queue → increases → decreases
- sentiment queue → increases → decreases  
- etc.

This shows tasks **flowing through the pipeline** ✅

### 4. See Full Job Status
```bash
curl http://localhost:8000/api/v1/jobs/{your_job_id}/detailed-status | python -m json.tool
```

Output shows:
- Progress percentage
- Current agent processing
- Which agents completed
- Queue depths per agent

---

## Expected Flow

```
BEFORE (Broken):
preprocessing ✅ → [STUCK] ❌ embedding not starting

AFTER (Fixed):
preprocessing ✅ → embedding 🔄 → sentiment 🔄 → theme 🔄 → bias 🔄 → recommendation 🔄 → ✅
```

---

## Console Logs You'll See

```
🔄 [Preprocessing Agent] Received task e7a7-1234...
✅ [Preprocessing Agent] → Handoff to [embedding]
📨 [embedding] Received task e7a7-1234...
✅ [embedding] → Handoff to [sentiment]
[cascade continues...]
🎉 Pipeline complete for e7a7-1234!
```

---

## Files Changed

| File | What Changed |
|------|--------------|
| `agents/orchestrator/task_worker.py` | **NEW** - Background worker that processes queues |
| `main.py` | Added task worker startup/shutdown |
| `api/routes.py` | Added `/worker/status` and `/jobs/{id}/detailed-status` |
| `frontend/app.py` | Better queue visualization |

---

## Test It Now!

1. Open terminal, run: `python main.py`
2. In another terminal: `curl http://localhost:8000/api/v1/worker/status`
3. In yet another: `streamlit run frontend/app.py`
4. Upload a test CSV with 10-20 rows
5. Watch queues update in real-time! 🎯

Your pipeline is now **alive and flowing**! 🚀
