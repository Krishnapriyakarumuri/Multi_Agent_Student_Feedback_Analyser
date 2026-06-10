# agents/orchestrator/agent_registry.py
from typing import Dict, List, Optional
from agents.base_agent import BaseAgent

class AgentRegistry:
    """Registry for discovering and managing agents"""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
    
    def register(self, name: str, agent: BaseAgent):
        """Register an agent"""
        self.agents[name] = agent
        print(f"📝 Registered agent: {name}")
    
    def unregister(self, name: str):
        """Remove an agent"""
        if name in self.agents:
            del self.agents[name]
    
    def get_agent(self, name: str) -> Optional[BaseAgent]:
        """Get agent by name"""
        return self.agents.get(name)
    
    def get_all_agents(self) -> Dict[str, BaseAgent]:
        """Get all registered agents"""
        return self.agents
    
    def get_agent_names(self) -> List[str]:
        """Get list of agent names"""
        return list(self.agents.keys())
    
    def get_agents_by_role(self, role: str) -> List[BaseAgent]:
        """Find agents by role"""
        return [a for a in self.agents.values() if role.lower() in a.role.lower()]