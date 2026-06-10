# agents/embedding_agent/agent.py
from agents.base_agent import BaseAgent
from agents.embedding_agent.tools import EmbeddingGenerator
from typing import Dict, Any

class EmbeddingAgent(BaseAgent):
    """
    Agent that generates semantic embeddings from text.
    Runs in parallel with Sentiment Agent.
    """
    
    def __init__(self):
        super().__init__(
            name="Embedding Agent",
            role="Semantic Understanding Specialist",
            tools=["embedding_generator", "semantic_similarity"]
        )
        self.generator = EmbeddingGenerator()
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        feedback_id = task.get("feedback_id", "unknown")
        text = task.get("cleaned_text", "")
        job_id = task.get("job_id", "unknown")
        
        self.think(f"Generating embedding for [{feedback_id}]", "start", f"Text length: {len(text)}")
        
        embedding = self.generator.generate(text)
        
        self.think(f"Embedding generated", "embedding_generator", f"Dimensions: {len(embedding)}")
        
        result = {
            "feedback_id": feedback_id,
            "embedding": embedding,
            "dimensions": len(embedding),
            "processed_by": self.name,
            "agent_id": self.agent_id
        }
        
        self.think("Embedding complete", "embedding_generator", "Ready for downstream agents")
        
        return result