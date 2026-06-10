# api/routes.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import uuid
import pandas as pd
import json
from api.schemas import *
from agents.orchestrator.orchestrator_agent import OrchestratorAgent
from memory.working_memory import WorkingMemory
from memory.long_term_memory import LongTermMemory
from communication.memory_bus import AgentMessageBus

router = APIRouter()
orchestrator = OrchestratorAgent()
working_memory = WorkingMemory()
long_term_memory = LongTermMemory()
# Use the orchestrator's message bus instance
message_bus = orchestrator.message_bus

# Initialize agents on startup
orchestrator.discover_and_register_agents()

@router.post("/feedback/upload", response_model=UploadResponse)
async def upload_feedback(file: UploadFile = File(...)):
    """
    Upload feedback CSV. Orchestrator agent delegates to specialized agents.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(400, "Only CSV files supported")
    
    df = pd.read_csv(file.file)
    
    if 'feedback_text' not in df.columns:
        raise HTTPException(400, "CSV must have 'feedback_text' column")
    
    job_id = str(uuid.uuid4())
    feedbacks = df['feedback_text'].dropna().tolist()
    
    # Orchestrator creates tasks for all agents
    task_ids = await orchestrator.create_analysis_task(
        job_id=job_id,
        feedbacks=feedbacks,
        metadata_columns=[c for c in df.columns if c != 'feedback_text']
    )
    
    agents = orchestrator.get_registered_agents()
    
    return UploadResponse(
        job_id=job_id,
        total_feedbacks=len(feedbacks),
        message=f"Orchestrator deployed {len(agents)} agents for analysis",
        agents_involved=agents,
        status_check_url=f"/api/v1/jobs/{job_id}/status"
    )

@router.get("/agents/status", response_model=AgentDashboardData)
async def get_agents_status():
    """Get status of all AI agents"""
    agents = orchestrator.get_registered_agents()
    agent_details = []
    
    for agent_name in agents:
        status = working_memory.get_agent_status(agent_name)
        agent_details.append(AgentInfo(
            name=agent_name,
            role=status.get("role", "unknown"),
            status=status.get("status", "offline"),
            tools=status.get("tools", []),
            messages_processed=int(status.get("messages_processed", 0))
        ))
    
    return AgentDashboardData(
        total_agents=len(agents),
        agents_online=sum(1 for a in agent_details if a.status == "online"),
        tasks_completed=working_memory.get_total_completed_tasks(),
        tasks_pending=working_memory.get_total_pending_tasks(),
        agent_details=agent_details
    )

@router.get("/jobs/{job_id}/status", response_model=TaskStatus)
async def get_job_status(job_id: str):
    """Check task status across all agents"""
    task = message_bus.tasks.get(job_id)
    
    if not task:
        raise HTTPException(404, "Task not found")
    
    completed = task.get("completed", [])
    pending = task.get("pending", [])
    total = len(completed) + len(pending)
    
    return TaskStatus(
        task_id=job_id,
        status=task.get("status", "in_progress"),
        progress=len(completed)/total*100 if total > 0 else 0,
        current_agent=task.get("current_agent", "preprocessing"),
        completed_agents=completed,
        pending_agents=pending
    )

@router.get("/jobs/{job_id}/results", response_model=List[AnalysisResult])
async def get_job_results(job_id: str):
    """Get complete multi-agent analysis results"""
    results = long_term_memory.get_analysis_results(job_id)
    
    if not results:
        raise HTTPException(404, "Results not found or still processing")
    
    return results

@router.get("/themes/current")
async def get_current_themes():
    """Get themes discovered by Theme Discovery Agent"""
    return long_term_memory.get_current_themes()

@router.get("/bias/report")
async def get_bias_report():
    """Get bias detection report from Bias Detection Agent"""
    return long_term_memory.get_bias_report()

@router.get("/recommendations/active")
async def get_recommendations():
    """Get recommendations from Recommendation Agent"""
    return long_term_memory.get_active_recommendations()

@router.get("/worker/status")
async def get_worker_status():
    """Get background task worker status and queue depths"""
    from fastapi import Request
    from starlette.requests import Request as StarletteRequest
    
    # This will show queue depths and processed tasks
    queue_depths = {}
    for agent_name in orchestrator.get_registered_agents():
        try:
            queue_depths[agent_name] = message_bus.get_queue_depth(agent_name)
        except:
            queue_depths[agent_name] = 0
    
    return {
        "message_bus_status": "active",
        "queue_depths": queue_depths,
        "total_tasks_in_pipeline": sum(queue_depths.values()),
        "tasks_in_memory_bus": len(message_bus.tasks)
    }

@router.get("/health")
async def health_check():
    """Quick health check endpoint"""
    return {"status": "ok", "message": "Server is running"}

@router.get("/jobs/{job_id}/detailed-status")
async def get_detailed_job_status(job_id: str):
    """Get detailed status showing which tasks are in which queue"""
    task = message_bus.tasks.get(job_id)
    
    if not task:
        raise HTTPException(404, "Job not found")
    
    return {
        "job_id": job_id,
        "description": task.get("description"),
        "status": task.get("status", "in_progress"),
        "total_feedbacks": len(task.get("agents", [])),
        "agents_involved": task.get("agents", []),
        "completed_agents": task.get("completed", []),
        "pending_agents": task.get("pending", []),
        "current_agent": task.get("current_agent"),
        "progress_percent": len(task.get("completed", [])) / len(task.get("agents", [1])) * 100 if task.get("agents") else 0,
        "created_at": task.get("created_at"),
        "queue_status": {
            agent: message_bus.get_queue_depth(agent)
            for agent in task.get("agents", [])
        }
    }