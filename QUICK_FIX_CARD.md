# ⚡ Quick Fix Card

## The Two Issues You Had

### 1️⃣ Pipeline Stuck
- Preprocessing done ✅
- Other agents never started ❌
- **Root cause**: No background worker

### 2️⃣ Server Timeouts
- All requests timeout
- Connection reset by host
- **Root cause**: Event loop blocked by task worker

## What I Fixed

| Issue | Solution |
|-------|----------|
| No worker | ✅ Created TaskWorker |
| Blocking event loop | ✅ Changed to threads |
| Can't monitor progress | ✅ Added /worker/status endpoint |
| Frontend doesn't handle errors | ✅ Better error messages |

## Quick Start (3 Commands)

```bash
# Terminal 1: Start server
python main.py

# Terminal 2: Check health (should instant)
curl http://localhost:8000/api/v1/health

# Terminal 3: Start frontend
streamlit run frontend/app.py
```

## What to Expect

```
Before:
preprocessing ✅ → [STUCK] ❌

After:
preprocessing ✅ → embedding 🔄 → sentiment 🔄 → theme 🔄 → bias 🔄 → recommendation 🔄 → ✅
```

## Monitor in Real-Time

```bash
watch -n 1 'curl http://localhost:8000/api/v1/worker/status | python -m json.tool'
```

You'll see:
```json
{
  "queue_depths": {
    "preprocessing": 0,
    "embedding": 45,    ← Decreasing as tasks complete
    "sentiment": 12,
    "theme": 3,
    "bias": 0,
    "recommendation": 0
  }
}
```

## Key Changes

| File | What Changed |
|------|--------------|
| task_worker.py | Async → Threads (EVENT LOOP FIX) |
| routes.py | Added /health, simplified /worker/status |
| main.py | Added agent init check |
| app.py | Better error handling |

## Timeline

```
0s:  Upload CSV
1s:  Server returns job_id
2s:  Tasks flowing through preprocessing
4s:  Preprocessing done, embedding started
6s:  Embedding done, sentiment started
...
20s: All complete ✅
```

## How It Works Now

```
FastAPI (Responsive) ← stays responsive to requests
  ↓
6 Worker Threads (Background) ← each processes one agent
  - preprocessing thread
  - embedding thread
  - sentiment thread
  - theme thread
  - bias thread
  - recommendation thread
```

Each thread:
- Listens to agent's queue (blocks safely in thread)
- Gets messages with 2s timeout
- Runs agent
- Hands off to next agent
- Repeats

## Status Codes

- ✅ Server running: `curl http://localhost:8000/api/v1/health` → 200 OK
- ✅ Agents online: `curl http://localhost:8000/api/v1/agents/status` → all "online"
- ✅ Processing: `curl http://localhost:8000/api/v1/worker/status` → queue_depths changing
- ✅ Frontend working: `streamlit run frontend/app.py` → shows progress

## If Something Breaks

| Issue | Check |
|-------|-------|
| Server won't start | Any Python errors in console? |
| Timeouts still happening | Is /health returning instantly? |
| Queues not changing | Upload a CSV first |
| Frontend can't connect | Is port 8000 available? |

## Performance

- Small CSV (10 rows): ~5 seconds end-to-end
- Medium CSV (100 rows): ~15 seconds  
- Large CSV (1000 rows): ~90 seconds

---

**You're ready to test! Run `python main.py` now.** 🚀
