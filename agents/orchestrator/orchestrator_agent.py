# agents/orchestrator/orchestrator_agent.py
from agents.base_agent import BaseAgent
from agents.preprocessing_agent.agent import PreprocessingAgent
from agents.embedding_agent.agent import EmbeddingAgent
from agents.sentiment_agent.agent import SentimentAgent
from agents.theme_agent.agent import ThemeDiscoveryAgent
from agents.bias_agent.agent import BiasDetectionAgent
from agents.recommendation_agent.agent import RecommendationAgent
from communication.memory_bus import AgentMessageBus
from typing import Dict, Any, List
import uuid

class OrchestratorAgent(BaseAgent):
    """
    Master coordinator of all AI agents.
    Breaks down tasks, delegates to specialists, aggregates results.
    """
    
    def __init__(self):
        super().__init__(
            name="Orchestrator Agent",
            role="Multi-Agent Workflow Coordination",
            tools=["task_decomposition", "agent_delegation", "result_aggregation"]
        )
        self.message_bus = AgentMessageBus()
        self.agents = {}
        self.is_active = True
    
    def discover_and_register_agents(self):
        """Discover and register all available agents"""
        self.agents = {
            "preprocessing": PreprocessingAgent(),
            "embedding": EmbeddingAgent(),
            "sentiment": SentimentAgent(),
            "theme": ThemeDiscoveryAgent(),
            "bias": BiasDetectionAgent(),
            "recommendation": RecommendationAgent()
        }
        
        for name, agent in self.agents.items():
            agent.is_active = True
            self.message_bus.update_agent_status(name, "online", {
                "role": agent.role,
                "tools": agent.tools
            })
        
        self.think(
            f"Registered {len(self.agents)} specialized agents",
            "agent_discovery",
            f"Agents: {list(self.agents.keys())}"
        )
    
    def get_registered_agents(self) -> List[str]:
        """Get list of registered agent names"""
        return list(self.agents.keys())
    
    async def create_analysis_task(self, job_id: str, feedbacks: List[str], metadata_columns: List[str] = None) -> List[str]:
        """Create analysis task and delegate to agents"""
        
        self.think(
            f"Creating analysis task {job_id[:8]}... with {len(feedbacks)} feedbacks",
            "task_creation",
            f"Will deploy {len(self.agents)} agents"
        )
        
        task_ids = []
        
        # Define agent pipeline order
        pipeline = ["preprocessing", "embedding", "sentiment", "theme", "bias", "recommendation"]
        
        # Register task in message bus
        self.message_bus.create_task(job_id, f"Analyze {len(feedbacks)} feedbacks", pipeline)
        
        # Delegate to preprocessing agent first
        for idx, feedback_text in enumerate(feedbacks):
            feedback_id = f"{job_id}_{idx}"
            
            task = {
                "task_id": f"{job_id}_task_{idx}",
                "job_id": job_id,
                "feedback_id": feedback_id,
                "text": feedback_text,
                "metadata": {},
                "pipeline": pipeline,
                "current_agent_index": 0
            }
            
            # Send to preprocessing agent
            self.message_bus.handoff(
                from_agent="orchestrator",
                to_agent="preprocessing",
                data=task,
                task_id=job_id
            )
            
            task_ids.append(task["task_id"])
        
        self.think(
            f"Delegated {len(task_ids)} tasks to preprocessing agent",
            "task_delegation",
            f"Pipeline: {' → '.join(pipeline)}"
        )
        
        return task_ids
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute orchestration task"""
        return {"status": "orchestrator_active", "agents": self.get_registered_agents()}