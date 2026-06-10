# agents/orchestrator/task_manager.py
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
import uuid

class TaskStatus(Enum):
    CREATED = "created"
    DELEGATED = "delegated"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class TaskManager:
    """Manages task lifecycle across agents"""
    
    def __init__(self):
        self.tasks: Dict[str, Dict] = {}
    
    def create_task(self, description: str, agents: List[str]) -> str:
        """Create a new task"""
        task_id = str(uuid.uuid4())
        self.tasks[task_id] = {
            "task_id": task_id,
            "description": description,
            "agents_involved": agents,
            "status": TaskStatus.CREATED,
            "current_agent": agents[0] if agents else None,
            "completed_agents": [],
            "agent_results": {},
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        return task_id
    
    def update_task(self, task_id: str, agent_name: str, status: TaskStatus, result: Dict = None):
        """Update task after agent completion"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task["status"] = status
            task["current_agent"] = agent_name
            task["completed_agents"].append(agent_name)
            if result:
                task["agent_results"][agent_name] = result
            task["updated_at"] = datetime.now().isoformat()
    
    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """Get task status"""
        return self.tasks.get(task_id)
    
    def get_pending_tasks(self) -> List[Dict]:
        """Get all pending tasks"""
        return [t for t in self.tasks.values() if t["status"] != TaskStatus.COMPLETED]
    
    def get_completed_tasks(self) -> List[Dict]:
        """Get all completed tasks"""
        return [t for t in self.tasks.values() if t["status"] == TaskStatus.COMPLETED]