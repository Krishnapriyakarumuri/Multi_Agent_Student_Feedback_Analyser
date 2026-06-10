# agents/sentiment_agent/agent.py
from agents.base_agent import BaseAgent
from agents.sentiment_agent.tools import SentimentAnalyzer
from typing import Dict, Any

class SentimentAgent(BaseAgent):
    """
    Agent that analyzes sentiment of feedback.
    Runs in parallel with Embedding Agent.
    """
    
    def __init__(self):
        super().__init__(
            name="Sentiment Agent",
            role="Emotional Intelligence Specialist",
            tools=["sentiment_analyzer"]
        )
        self.analyzer = SentimentAnalyzer()
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        feedback_id = task.get("feedback_id", "unknown")
        text = task.get("cleaned_text", "")
        job_id = task.get("job_id", "unknown")
        
        self.think(f"Analyzing sentiment for [{feedback_id}]", "start", "")
        
        sentiment = self.analyzer.analyze(text)
        
        self.think(f"Sentiment: {sentiment['label']}", "sentiment_analyzer", f"Confidence: {sentiment['confidence']}")
        
        result = {
            "feedback_id": feedback_id,
            "sentiment": sentiment,
            "processed_by": self.name,
            "agent_id": self.agent_id
        }
        
        self.think("Sentiment analysis complete", "sentiment_analyzer", f"Result: {sentiment['label']}")
        
        return result