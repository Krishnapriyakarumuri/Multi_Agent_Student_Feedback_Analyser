# agents/theme_agent/agent.py
from agents.base_agent import BaseAgent
from agents.theme_agent.tools import ThemeClusterer
from typing import Dict, Any

class ThemeDiscoveryAgent(BaseAgent):
    """
    Agent that discovers themes from embeddings.
    Receives from Embedding Agent.
    """
    
    def __init__(self):
        super().__init__(
            name="Theme Discovery Agent",
            role="Pattern Recognition Specialist",
            tools=["theme_clusterer"]
        )
        self.clusterer = ThemeClusterer()
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        feedback_id = task.get("feedback_id", "unknown")
        embedding = task.get("embedding", [])
        job_id = task.get("job_id", "unknown")
        
        self.think(f"Assigning theme for [{feedback_id}]", "start", f"Vector dims: {len(embedding)}")
        
        theme = self.clusterer.assign_topic(embedding)
        
        self.think(f"Theme: {theme['topic_name']}", "theme_clusterer", f"Keywords: {theme['keywords'][:5]}")
        
        result = {
            "feedback_id": feedback_id,
            "theme": theme,
            "processed_by": self.name,
            "agent_id": self.agent_id
        }
        
        self.think("Theme assignment complete", "theme_clusterer", f"Topic: {theme['topic_name']}")
        
        return result