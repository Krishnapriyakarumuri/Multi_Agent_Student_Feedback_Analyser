# agents/base_agent.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid
import asyncio

@dataclass
class AgentMemory:
    """Agent's working memory during a task"""
    task_id: str
    context: Dict[str, Any] = field(default_factory=dict)
    observations: List[Dict] = field(default_factory=list)
    decisions: List[Dict] = field(default_factory=list)
    errors: List[Dict] = field(default_factory=list)

@dataclass
class AgentThought:
    """Agent's reasoning step"""
    thought: str
    action: str
    observation: str
    timestamp: datetime = field(default_factory=datetime.now)

class BaseAgent(ABC):
    """
    Base class for all AI agents in the system.
    Each agent has:
    - Role: What it does
    - Tools: What it can use
    - Memory: What it remembers
    - System Prompt: How it thinks
    """
    
    def __init__(self, name: str, role: str, tools: List[str] = None):
        self.agent_id = str(uuid.uuid4())[:8]
        self.name = name
        self.role = role
        self.tools = tools or []
        self.memory = None
        self.thought_chain: List[AgentThought] = []
    
    @property
    def system_prompt(self) -> str:
        """Define the agent's system prompt"""
        return f"""
        You are {self.name}, an AI agent specialized in {self.role}.
        Your goal is to execute your task with precision and report results.
        
        Available tools: {', '.join(self.tools)}
        
        Guidelines:
        1. Think step by step before acting
        2. Validate your outputs
        3. Report errors transparently
        4. Pass clean data to downstream agents
        """
    
    def think(self, thought: str, action: str = "", observation: str = ""):
        """Record agent's thought process"""
        step = AgentThought(
            thought=thought,
            action=action,
            observation=observation
        )
        self.thought_chain.append(step)
        print(f"🤔 [{self.name}] {thought}")
        return step
    
    @abstractmethod
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent's task.
        Each agent implements its own logic.
        """
        pass
    
    def report(self) -> Dict[str, Any]:
        """Generate agent's execution report"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "role": self.role,
            "tools_used": self.tools,
            "thoughts": len(self.thought_chain),
            "success": len([t for t in self.thought_chain if "error" not in t.observation.lower()]),
            "errors": len([t for t in self.thought_chain if "error" in t.observation.lower()])
        }
    
    def __repr__(self):
        return f"🤖 {self.name} ({self.role})"
    


# # agents/base_agent.py
# from abc import ABC, abstractmethod
# from typing import Dict, Any, List, Optional
# from dataclasses import dataclass, field
# from datetime import datetime
# import uuid

# @dataclass
# class AgentThought:
#     """Records agent's reasoning process"""
#     thought: str
#     action: str = ""
#     observation: str = ""
#     timestamp: datetime = field(default_factory=datetime.now)
    
#     def __str__(self):
#         return f"🤔 {self.thought} → {self.action} → {self.observation}"

# class BaseAgent(ABC):
#     """
#     Base class for all AI agents.
    
#     Each agent has:
#     - Identity (name, role, agent_id)
#     - System Prompt (defines behavior)
#     - Tools (what it can do)
#     - Memory (what it remembers)
#     - Thought Chain (how it reasons)
#     """
    
#     def __init__(self, name: str, role: str, tools: List[str] = None):
#         self.agent_id = f"agent-{str(uuid.uuid4())[:8]}"
#         self.name = name
#         self.role = role
#         self.tools = tools or []
#         self.thought_chain: List[AgentThought] = []
#         self.is_active = False
    
#     @property
#     def system_prompt(self) -> str:
#         """Define how the agent thinks and behaves"""
#         return f"""
#         You are {self.name}, an AI agent specialized in: {self.role}
#         Available tools: {', '.join(self.tools)}
#         Always think step-by-step, validate outputs, and report clearly.
#         """
    
#     def think(self, thought: str, action: str = "", observation: str = ""):
#         """Record agent's reasoning"""
#         step = AgentThought(thought=thought, action=action, observation=observation)
#         self.thought_chain.append(step)
#         print(f"[{self.name}] {step}")
#         return step
    
#     @abstractmethod
#     async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
#         """Execute agent's main task. Must be implemented by each agent."""
#         pass
    
#     def get_status(self) -> Dict[str, Any]:
#         """Get agent's current status"""
#         return {
#             "agent_id": self.agent_id,
#             "name": self.name,
#             "role": self.role,
#             "tools": self.tools,
#             "thoughts_processed": len(self.thought_chain),
#             "is_active": self.is_active
#         }
    
#     def __repr__(self):
#         return f"🤖 {self.name} | {self.role} | Tools: {len(self.tools)}"