# memory/agent_state.py
from typing import Dict, Any
from datetime import datetime
from enum import Enum

class AgentStatus(Enum):
    IDLE = "idle"
    PROCESSING = "processing"
    WAITING = "waiting"
    ERROR = "error"
    OFFLINE = "offline"

class AgentState:
    """Tracks state of each agent"""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.status = AgentStatus.IDLE
        self.current_task = None
        self.tasks_completed = 0
        self.tasks_failed = 0
        self.last_active = datetime.now()
        self.thought_chain = []
    
    def update_status(self, status: AgentStatus, task_id: str = None):
        self.status = status
        self.current_task = task_id
        self.last_active = datetime.now()
    
    def record_completion(self):
        self.tasks_completed += 1
        self.status = AgentStatus.IDLE
        self.last_active = datetime.now()
    
    def record_failure(self):
        self.tasks_failed += 1
        self.status = AgentStatus.ERROR
        self.last_active = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent": self.agent_name,
            "status": self.status.value,
            "current_task": self.current_task,
            "completed": self.tasks_completed,
            "failed": self.tasks_failed,
            "last_active": self.last_active.isoformat()
        }