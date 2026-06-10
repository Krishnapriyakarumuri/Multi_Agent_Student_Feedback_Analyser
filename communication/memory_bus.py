# communication/memory_bus.py
"""
In-memory message bus for agent communication.
Pure Python - No Redis required!
"""

import queue
import threading
from typing import Dict, Any, Optional, List
from datetime import datetime
from collections import defaultdict
import json

class AgentMessage:
    def __init__(self, sender: str, receiver: str, message_type: str, payload: Dict, task_id: str = None):
        self.sender = sender
        self.receiver = receiver
        self.message_type = message_type
        self.payload = payload
        self.task_id = task_id
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "message_type": self.message_type,
            "payload": self.payload,
            "task_id": self.task_id,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'AgentMessage':
        return cls(
            data.get("sender", "unknown"),
            data.get("receiver", "unknown"),
            data.get("message_type", "unknown"),
            data.get("payload", {}),
            data.get("task_id")
        )

class InMemoryMessageBus:
    """Pure Python message bus - No Redis needed!"""
    
    def __init__(self):
        self.agent_queues: Dict[str, queue.Queue] = defaultdict(queue.Queue)
        self.agent_status: Dict[str, Dict] = {}
        self.tasks: Dict[str, Dict] = {}
        self.lock = threading.Lock()
        print("📨 In-Memory Message Bus initialized (No Redis required)")
    
    def send_message(self, message: AgentMessage):
        self.agent_queues[message.receiver].put(message.to_dict())
    
    def receive_message(self, agent_name: str, timeout: int = 5) -> Optional[AgentMessage]:
        try:
            data = self.agent_queues[agent_name].get(timeout=timeout)
            return AgentMessage.from_dict(data)
        except queue.Empty:
            return None
    
    def handoff(self, from_agent: str, to_agent: str, data: Dict, task_id: str):
        msg = AgentMessage(from_agent, to_agent, "handoff", data, task_id)
        self.send_message(msg)
        
        if task_id not in self.tasks:
            self.tasks[task_id] = {"handoffs": [], "status": "in_progress"}
        
        # Ensure handoffs key exists
        if "handoffs" not in self.tasks[task_id]:
            self.tasks[task_id]["handoffs"] = []
        
        self.tasks[task_id]["handoffs"].append({
            "from": from_agent,
            "to": to_agent,
            "timestamp": datetime.now().isoformat()
        })
        print(f"🤝 Handoff: [{from_agent}] → [{to_agent}]")
    
    def update_agent_status(self, agent_name: str, status: str, details: Dict = None):
        self.agent_status[agent_name] = {
            "status": status,
            "last_updated": datetime.now().isoformat(),
            "details": details or {},
            "messages_processed": self.agent_status.get(agent_name, {}).get("messages_processed", 0) + 1
        }
    
    def get_agent_status(self, agent_name: str) -> Dict:
        return self.agent_status.get(agent_name, {"status": "offline"})
    
    def create_task(self, task_id: str, description: str, agents: list):
        self.tasks[task_id] = {
            "description": description,
            "status": "in_progress",
            "agents": agents,
            "completed": [],
            "pending": agents.copy(),
            "current_agent": agents[0] if agents else "none",
            "created_at": datetime.now().isoformat()
        }
    
    def update_task_progress(self, task_id: str, agent_name: str):
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task["completed"].append(agent_name)
            if agent_name in task["pending"]:
                task["pending"].remove(agent_name)
            task["current_agent"] = task["pending"][0] if task["pending"] else "done"
            if not task["pending"]:
                task["status"] = "completed"
    
    def get_task_status(self, task_id: str) -> Dict:
        task = self.tasks.get(task_id, {})
        return {
            "status": task.get("status", "unknown"),
            "completed_agents": json.dumps(task.get("completed", [])),
            "pending_agents": json.dumps(task.get("pending", [])),
            "current_agent": task.get("current_agent", ""),
            "progress": len(task.get("completed", [])) / len(task.get("agents", [1])) * 100 if task.get("agents") else 0
        }
    
    def get_all_agents(self) -> list:
        return list(self.agent_status.keys())
    
    def get_queue_depth(self, agent_name: str) -> int:
        return self.agent_queues[agent_name].qsize()

# Create a global instance
AgentMessageBus = InMemoryMessageBus