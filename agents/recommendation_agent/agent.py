# agents/recommendation_agent/agent.py
from agents.base_agent import BaseAgent
from typing import Dict, Any
import json
import time

class RecommendationAgent(BaseAgent):
    """
    Agent responsible for generating actionable recommendations.
    Final agent in the pipeline.
    """
    
    def __init__(self):
        super().__init__(
            name="Recommendation Agent",
            role="Strategic Advisor & Action Generator",
            tools=["gpt_reasoner", "context_synthesizer"]
        )
        self.client = None
    
    @property
    def system_prompt(self) -> str:
        return """
        You are the Recommendation Agent - the strategic brain of our system.
        Generate actionable recommendations in JSON format.
        """
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Generate recommendations with context from upstream agents"""
        
        feedback_id = task.get("feedback_id", "unknown")
        theme = task.get("theme", {})
        sentiment = task.get("sentiment", {})
        bias = task.get("bias_guardrails", "")
        
        self.think(f"Generating recommendation for [{feedback_id}]", "start", "")
        
        if task.get("is_biased"):
            self.think("Bias guardrails active", "bias_check", "Ensuring fairness")
        
        # Generate recommendation (with GPT or demo fallback)
        result = self._generate_recommendation(theme, sentiment, bias)
        
        self.think(f"Recommendation: {result.get('recommendation', '')[:100]}...", "done", f"Priority: {result.get('priority')}")
        
        return {
            "feedback_id": feedback_id,
            "recommendation_text": result.get("recommendation", ""),
            "priority": result.get("priority", "medium"),
            "action_items": result.get("action_items", []),
            "expected_impact": result.get("expected_impact", ""),
            "fairness_note": result.get("fairness_note", ""),
            "upstream_agents": ["Preprocessing", "Sentiment", "Theme Discovery", "Bias Detection"],
            "processed_by": self.name,
            "agent_id": self.agent_id
        }
    
    def _generate_recommendation(self, theme, sentiment, bias):
        """Generate recommendation - uses GPT or falls back to demo mode"""
        
        theme_name = theme.get("topic_name", theme.get("theme_name", "Unknown"))
        keywords = theme.get("keywords", [])
        sentiment_label = sentiment.get("label", "neutral")
        
        # Try GPT first, fallback to demo
        try:
            from openai import AzureOpenAI
            from config import config
            
            if config.AZURE_OPENAI_KEY and "demo" not in config.AZURE_OPENAI_KEY:
                if self.client is None:
                    self.client = AzureOpenAI(
                        api_key=config.AZURE_OPENAI_KEY,
                        api_version="2024-02-15-preview",
                        azure_endpoint=config.AZURE_OPENAI_ENDPOINT
                    )
                
                prompt = f"""
                Theme: {theme_name}
                Keywords: {keywords[:10]}
                Sentiment: {sentiment_label}
                Bias Notes: {bias if bias else 'None'}
                
                Generate recommendation in JSON format with:
                recommendation, priority, action_items, expected_impact, fairness_note
                """
                
                response = self.client.chat.completions.create(
                    model=config.GPT_MODEL,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=300,
                    temperature=0.7,
                    response_format={"type": "json_object"}
                )
                return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"GPT not available: {e}")
        
        # Demo fallback recommendations
        return self._demo_recommendation(theme_name, sentiment_label)
    
    def _demo_recommendation(self, theme, sentiment):
        """Generate demo recommendations without GPT"""
        
        demo_recs = {
            "placement": {
                "recommendation": "Enhance placement preparation with structured training programs and mock interviews",
                "priority": "high",
                "action_items": [
                    "Conduct weekly mock interviews with industry experts",
                    "Create a placement preparation module with updated materials",
                    "Establish a dedicated placement mentorship program",
                    "Organize company-specific preparation workshops",
                    "Track placement readiness through regular assessments"
                ],
                "expected_impact": "Improved student confidence and placement success rate",
                "fairness_note": "Recommendations are inclusive and accessible to all students"
            },
            "library": {
                "recommendation": "Modernize library resources and improve accessibility",
                "priority": "medium",
                "action_items": [
                    "Update book collection based on student recommendations",
                    "Extend library operating hours",
                    "Improve digital resource access",
                    "Create quiet study zones"
                ],
                "expected_impact": "Better learning environment and resource utilization",
                "fairness_note": "Resources accessible to all students equally"
            },
            "default": {
                "recommendation": f"Address student concerns regarding {theme} based on {sentiment} feedback",
                "priority": "medium",
                "action_items": [
                    "Conduct detailed survey to understand specific issues",
                    "Form a student-faculty committee to address concerns",
                    "Implement improvements and track progress",
                    "Regular feedback collection to measure impact"
                ],
                "expected_impact": "Improved student satisfaction",
                "fairness_note": "All recommendations are inclusive and equitable"
            }
        }
        
        # Match theme to demo recommendation
        theme_lower = theme.lower()
        for key in demo_recs:
            if key in theme_lower:
                return demo_recs[key]
        
        return demo_recs["default"]