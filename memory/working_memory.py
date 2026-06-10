# memory/working_memory.py
"""
Working memory for agents using in-memory storage.
No Redis required - uses Python dictionaries.
"""

import json
from typing import Dict, Any, Optional
from datetime import datetime
from collections import defaultdict

class WorkingMemory:
    """Short-term memory for agents (In-Memory, No Redis)"""
    
    def __init__(self):
        self.store: Dict[str, Any] = {}
        self.agent_status: Dict[str, Dict] = defaultdict(dict)
        self.tasks: Dict[str, Dict] = {}
        self.embeddings: Dict[str, list] = {}
        self.expiry: Dict[str, float] = {}
        print("🧠 Working Memory initialized (In-Memory)")
    
    def set(self, key: str, value: Any, ttl: int = 3600):
        """Store a value with optional TTL"""
        self.store[key] = json.dumps(value, default=str)
        if ttl:
            import time
            self.expiry[key] = time.time() + ttl
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value, checking expiry"""
        import time
        if key in self.expiry and time.time() > self.expiry[key]:
            self.delete(key)
            return None
        val = self.store.get(key)
        return json.loads(val) if val else None
    
    def delete(self, key: str):
        """Delete a key"""
        self.store.pop(key, None)
        self.expiry.pop(key, None)
    
    def get_agent_status(self, agent_name: str) -> Dict:
        """Get agent status from in-memory store"""
        return self.agent_status.get(agent_name, {
            "status": "offline",
            "role": "unknown",
            "tools": [],
            "messages_processed": 0
        })
    
    def update_agent_status(self, agent_name: str, status: str, details: Dict = None):
        """Update agent status"""
        current = self.agent_status.get(agent_name, {})
        self.agent_status[agent_name] = {
            "status": status,
            "role": details.get("role", current.get("role", "")) if details else current.get("role", ""),
            "tools": details.get("tools", current.get("tools", [])) if details else current.get("tools", []),
            "messages_processed": current.get("messages_processed", 0) + 1,
            "last_updated": datetime.now().isoformat()
        }
    
    def get_task_status(self, task_id: str) -> Dict:
        """Get task status"""
        return self.tasks.get(task_id, {})
    
    def set_task_status(self, task_id: str, status: Dict):
        """Set task status"""
        self.tasks[task_id] = status
    
    def get_total_completed_tasks(self) -> int:
        """Count completed tasks"""
        return sum(1 for t in self.tasks.values() if t.get("status") == "completed")
    
    def get_total_pending_tasks(self) -> int:
        """Count pending tasks"""
        return sum(1 for t in self.tasks.values() if t.get("status") not in ["completed", "failed"])
    
    def cache_embedding(self, text_hash: str, embedding: list):
        """Cache an embedding vector"""
        self.embeddings[text_hash] = embedding
    
    def get_cached_embedding(self, text_hash: str) -> Optional[list]:
        """Get cached embedding"""
        return self.embeddings.get(text_hash)