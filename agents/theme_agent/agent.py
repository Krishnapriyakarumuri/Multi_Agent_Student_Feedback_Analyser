# agents/theme_agent/agent.py
from agents.base_agent import BaseAgent
from agents.theme_agent.tools import ThemeClusterer
from typing import Dict, Any

class ThemeDiscoveryAgent(BaseAgent):
    """
    Agent that discovers themes from embeddings (and text).

    Phase 1 (batch, optional):
        Call `agent.clusterer.fit_topics(texts, embeddings)` once per job
        before processing individual items — this trains BERTopic and
        generates Groq LLM theme labels.

    Phase 2 (per-item):
        `execute()` receives the embedding (+ cleaned_text) produced by
        EmbeddingAgent and assigns the feedback to the closest theme via
        BERTopic `transform`; falls back to keyword matching if not fitted.

    Receives from: Embedding Agent
    Sends to: Bias Detection Agent
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
        embedding   = task.get("embedding", [])
        text        = task.get("cleaned_text", "")   # forwarded from PreprocessingAgent
        job_id      = task.get("job_id", "unknown")

        self.think(
            f"Assigning theme for [{feedback_id}]",
            "start",
            f"Vector dims: {len(embedding)} | BERTopic fitted: {self.clusterer.is_fitted}"
        )

        # Per-item inference — BERTopic transform if fitted, keyword fallback otherwise
        theme = self.clusterer.assign_topic(embedding, text)

        self.think(
            f"Theme: {theme['topic_name']} (method={theme['method']})",
            "theme_clusterer",
            f"Keywords: {theme['keywords'][:3]} | p={theme['probability']:.2f}"
        )

        result = {
            "feedback_id": feedback_id,
            "theme": theme,
            "processed_by": self.name,
            "agent_id": self.agent_id
        }

        self.think(
            "Theme assignment complete",
            "theme_clusterer",
            f"Topic: {theme['topic_name']} | Outlier: {theme['is_outlier']}"
        )

        return result