# agents/recommendation_agent/agent.py
from agents.base_agent import BaseAgent
from typing import Dict, Any
import json
import time
import groq
from config import config

class RecommendationAgent(BaseAgent):
    """
    Agent responsible for generating actionable recommendations.
    Final agent in the pipeline.
    """
    
    def __init__(self):
        super().__init__(
            name="Recommendation Agent",
            role="Strategic Advisor & Action Generator",
            tools=["groq_reasoner", "context_synthesizer"]
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
        """Generate recommendation - uses Groq or falls back to demo mode"""
        
        theme_name = theme.get("topic_name", theme.get("theme_name", "Unknown"))
        keywords = theme.get("keywords", [])
        sentiment_label = sentiment.get("label", "neutral")
        
        # Try Groq first, fallback to demo
        try:
            
            if config.GROQ_API_KEY and config.GROQ_API_KEY.strip():
                if self.client is None:
                    self.client = groq.Groq(api_key=config.GROQ_API_KEY)
                
                prompt = f"""Theme: {theme_name}
Keywords: {keywords[:10]}
Sentiment: {sentiment_label}
Bias Notes: {bias if bias else 'None'}

Generate a recommendation as a JSON object with these exact keys:
- recommendation: Main recommendation (2-3 sentences)
- priority: one of "high", "medium", or "low"
- action_items: list of 3-5 specific actionable steps
- expected_impact: what improvement to expect
- fairness_note: how bias was considered (if applicable)

Return ONLY valid JSON, no extra text."""
                
                response = self.client.chat.completions.create(
                    model=config.GROQ_MODEL,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=config.GPT_MAX_TOKENS,
                    temperature=config.GPT_TEMPERATURE,
                    response_format={"type": "json_object"}
                )
                return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Groq not available: {e}")
        
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