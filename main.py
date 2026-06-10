# main.py - Auto-detects available services
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
from api.routes import router, orchestrator
from config import config
from agents.orchestrator.task_worker import TaskWorker
import asyncio
import sys

# Check dependencies
print("=" * 60)
print("🔍 Checking System Dependencies...")
print("=" * 60)

# Check SQLite
try:
    import sqlite3
    print("✅ SQLite: Available (built-in)")
except:
    print("❌ SQLite: Not available")

# Check Redis
try:
    import redis
    r = redis.Redis.from_url(config.REDIS_URL, socket_connect_timeout=2)
    r.ping()
    print("✅ Redis: Connected")
except:
    print("⚠️ Redis: Not available - Using In-Memory Queue")
    config.REDIS_URL = "memory://"

# Check Azure OpenAI
if config.AZURE_OPENAI_KEY and "demo" not in config.AZURE_OPENAI_KEY:
    print("✅ Azure OpenAI: Configured")
else:
    print("⚠️ Azure OpenAI: Using demo key (recommendations will be simulated)")

print("=" * 60)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("\n🚀 Starting Multi-Agent System...")
    print(f"📦 Database: {config.DATABASE_URL}")
    print(f"📨 Queue: {'Redis' if 'memory' not in config.REDIS_URL else 'In-Memory'}")
    
    # Give agents a moment to initialize
    await asyncio.sleep(0.5)
    
    # Verify agents are initialized
    agents_list = orchestrator.get_registered_agents()
    print(f"✅ {len(agents_list)} agents registered: {agents_list}")
    
    if not agents_list:
        print("❌ ERROR: No agents registered!")
        raise RuntimeError("Agents failed to initialize")
    
    # Start background task worker (agents already initialized by routes.py)
    # CRITICAL: Pass the orchestrator's message_bus so messages go to the same queue!
    task_worker = TaskWorker(orchestrator.agents, message_bus=orchestrator.message_bus)
    worker_task = asyncio.create_task(task_worker.start())
    app.state.task_worker = task_worker
    
    print("⚡ Background Task Worker started - Processing agent pipeline...")
    print("📡 API ready at http://localhost:8000")
    
    yield
    
    # Shutdown
    print("\n👋 Shutting down...")
    await task_worker.stop()
    worker_task.cancel()
    try:
        await worker_task
    except asyncio.CancelledError:
        pass

app = FastAPI(
    title="Multi-Agent Feedback Analyzer",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "system": "Multi-Agent Feedback Analysis",
        "database": "SQLite" if "sqlite" in config.DATABASE_URL else "PostgreSQL",
        "queue": "In-Memory" if "memory" in config.REDIS_URL else "Redis",
        "agents": 6
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)