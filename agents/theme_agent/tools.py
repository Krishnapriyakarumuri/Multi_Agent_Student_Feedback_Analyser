# agents/theme_agent/tools.py
from typing import List, Dict, Optional
import numpy as np
import os
from groq import Groq
from bertopic import BERTopic
from bertopic.representation import KeyBERTInspired
from umap import UMAP
from hdbscan import HDBSCAN

class ThemeClusterer:
    """
    Tool: Assigns feedback to themes using BERTopic + Groq LLM labels.

    Two-phase design that fits the per-item agent architecture:
      Phase 1 (batch)   — fit_topics(texts, embeddings)  called once per job
      Phase 2 (per-item) — assign_topic(embedding, text)  called by the agent
    Falls back to keyword matching (then hash) when BERTopic is not fitted yet.
    """

    def __init__(self, groq_api_key: Optional[str] = None):
        from config import config

        self.config = config
        self.topic_model = None
        self.topic_labels: Dict[int, str] = {}
        self.is_fitted = False
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY", "")
        self._groq_client = None

        # Keyword templates used as fallback when BERTopic is not fitted
        self.theme_templates = {
            "Teaching Quality": {
                "keywords": ["explanation", "clear", "understanding", "teaching",
                             "lecture", "material", "delivery", "instructor", "professor"]
            },
            "Course Structure": {
                "keywords": ["organization", "curriculum", "structure", "flow",
                             "progression", "syllabus", "schedule", "outline", "module"]
            },
            "Engagement": {
                "keywords": ["interesting", "engaging", "motivating", "boring",
                             "interactive", "participation", "involved", "activity", "discussion"]
            },
            "Difficulty Level": {
                "keywords": ["hard", "easy", "challenging", "difficult", "simple",
                             "complex", "level", "pace", "overwhelming", "manageable"]
            },
            "Assignment Quality": {
                "keywords": ["assignment", "homework", "project", "exercise",
                             "task", "practical", "work", "submission", "deadline"]
            },
            "Feedback & Support": {
                "keywords": ["feedback", "support", "help", "available", "response",
                             "communication", "accessible", "office hours", "doubt"]
            },
            "Resources": {
                "keywords": ["materials", "resources", "textbook", "reading",
                             "slides", "content", "access", "notes", "reference"]
            }
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _groq_client_init(self):
        """Lazy-initialise the Groq client."""
        if self._groq_client is None and self.groq_api_key:
            self._groq_client = Groq(api_key=self.groq_api_key)
        return self._groq_client

    def _build_topic_model(self, embedding_model=None):
        """Construct BERTopic with UMAP + HDBSCAN + KeyBERT representation."""
        umap_model = UMAP(
            n_neighbors=15,
            n_components=5,
            min_dist=0.0,
            metric="cosine",
            random_state=42
        )

        hdbscan_model = HDBSCAN(
            min_cluster_size=self.config.MIN_TOPIC_SIZE,
            min_samples=5,
            prediction_data=True
        )

        self.topic_model = BERTopic(
            representation_model=KeyBERTInspired(),
            umap_model=umap_model,
            hdbscan_model=hdbscan_model,
            min_topic_size=self.config.MIN_TOPIC_SIZE,
            calculate_probabilities=True,
            embedding_model=embedding_model     # None → BERTopic won't re-embed
        )
        return self.topic_model

    # ------------------------------------------------------------------
    # Phase 1: Batch fitting (called once per job by orchestrator)
    # ------------------------------------------------------------------

    def fit_topics(
        self,
        texts: List[str],
        embeddings: np.ndarray,
        nr_topics: int = 8,
        embedding_model=None
    ) -> List[int]:
        """
        Fit BERTopic on the full batch of texts + pre-computed embeddings.
        Reduces to `nr_topics` themes and generates Groq LLM labels.

        Args:
            texts: List of cleaned feedback strings.
            embeddings: 2-D numpy array (n_samples × embedding_dim).
            nr_topics: Target number of topics after reduction.
            embedding_model: Optional SentenceTransformer used by BERTopic
                             (pass None when supplying pre-computed embeddings).

        Returns:
            List of integer topic IDs, one per text.
        """
        min_needed = self.config.MIN_TOPIC_SIZE * 2
        if len(texts) < min_needed:
            print(f"⚠️  Only {len(texts)} texts — need ≥{min_needed} for BERTopic. "
                  f"Using keyword-based fallback.")
            return [-1] * len(texts)

        print(f"🔍 Fitting BERTopic on {len(texts)} texts …")
        self._build_topic_model(embedding_model)

        # Step 1 — initial fit
        topics, _ = self.topic_model.fit_transform(texts, np.array(embeddings))

        # Step 2 — reduce topics
        unique_non_outlier = len(set(t for t in topics if t != -1))
        if nr_topics and unique_non_outlier > nr_topics:
            self.topic_model.reduce_topics(texts, nr_topics=nr_topics)
            topics = self.topic_model.topics_

        self.is_fitted = True
        print(f"✅ BERTopic fitted — {len(set(topics))} topics discovered")

        # Step 3 — label topics via Groq
        self.generate_theme_labels()

        return list(topics)

    # ------------------------------------------------------------------
    # Phase 1b: LLM label generation
    # ------------------------------------------------------------------

    def generate_theme_labels(self) -> Dict[int, str]:
        """
        Generate 2-3 word human-readable labels for each topic using Groq.
        Falls back to top-2 keywords when Groq is unavailable.
        """
        if not self.is_fitted:
            return {}

        topic_info = self.topic_model.get_topic_info()
        client = self._groq_client_init()

        for topic_id in topic_info["Topic"]:
            if topic_id == -1:
                self.topic_labels[topic_id] = "Miscellaneous"
                continue

            raw_keywords = self.topic_model.get_topic(topic_id) or []
            keywords = [word for word, _ in raw_keywords[:5]]

            if client:
                try:
                    prompt = (
                        "Generate a 2-3 word dashboard theme name.\n\n"
                        f"Keywords: {', '.join(keywords)}\n\n"
                        "Rules:\n"
                        "- Max 3 words\n"
                        "- Professional tone\n"
                        "- College feedback domain\n"
                        "- Return ONLY the name, nothing else"
                    )
                    response = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0
                    )
                    label = response.choices[0].message.content.strip()
                except Exception as exc:
                    print(f"⚠️  Groq label failed for topic {topic_id}: {exc}")
                    label = " ".join(keywords[:2]).title()
            else:
                label = " ".join(keywords[:2]).title()

            self.topic_labels[topic_id] = label

        self.topic_model.set_topic_labels(self.topic_labels)
        print(f"🏷️  Theme labels generated: {self.topic_labels}")
        return self.topic_labels

    # ------------------------------------------------------------------
    # Phase 2: Per-item inference (called by ThemeDiscoveryAgent)
    # ------------------------------------------------------------------

    def assign_topic(self, embedding: List[float], text: str = "") -> Dict:
        """
        Assign a single feedback item to a theme.
        Uses BERTopic `transform` when fitted; otherwise falls back gracefully.
        """
        if self.is_fitted and self.topic_model is not None:
            return self._assign_via_bertopic(embedding, text)
        return self._assign_via_keywords(embedding, text)

    def _assign_via_bertopic(self, embedding: List[float], text: str) -> Dict:
        """Per-item BERTopic prediction using transform()."""
        try:
            doc = text if text else "feedback"
            emb_array = np.array([embedding])
            topics, probs = self.topic_model.transform([doc], emb_array)

            topic_id = int(topics[0])
            prob_arr = np.array(probs[0]) if probs is not None else np.array([0.75])
            probability = float(prob_arr.max())

            topic_name = self.topic_labels.get(topic_id, "Miscellaneous")
            raw_kw = self.topic_model.get_topic(topic_id) or []
            keywords = [w for w, _ in raw_kw[:5]]

            return {
                "topic_id": topic_id,
                "topic_name": topic_name,
                "keywords": keywords,
                "probability": probability,
                "is_outlier": topic_id == -1,
                "embedding_dims": len(embedding),
                "method": "bertopic"
            }
        except Exception as exc:
            print(f"⚠️  BERTopic transform error: {exc} — falling back to keywords")
            return self._assign_via_keywords(embedding, text)

    def _assign_via_keywords(self, embedding: List[float], text: str) -> Dict:
        """
        Keyword-overlap topic assignment — used when BERTopic is not fitted.
        Falls back to deterministic hash assignment when no keywords match.
        """
        if text:
            text_lower = text.lower()
            best_theme, best_score = None, 0

            for theme_name, theme_data in self.theme_templates.items():
                score = sum(1 for kw in theme_data["keywords"] if kw in text_lower)
                if score > best_score:
                    best_score = score
                    best_theme = theme_name

            if best_theme and best_score > 0:
                topic_id = list(self.theme_templates.keys()).index(best_theme)
                return {
                    "topic_id": topic_id,
                    "topic_name": best_theme,
                    "keywords": self.theme_templates[best_theme]["keywords"][:5],
                    "probability": min(0.5 + best_score * 0.1, 0.95),
                    "is_outlier": False,
                    "embedding_dims": len(embedding),
                    "method": "keyword"
                }

        # Final fallback: deterministic hash on embedding bytes
        import hashlib
        emb_hash = int(hashlib.md5(np.array(embedding).tobytes()).hexdigest(), 16)
        theme_names = list(self.theme_templates.keys())
        selected = theme_names[emb_hash % len(theme_names)]
        topic_id = emb_hash % len(theme_names)

        return {
            "topic_id": topic_id,
            "topic_name": selected,
            "keywords": self.theme_templates[selected]["keywords"][:5],
            "probability": 0.75 + (emb_hash % 25) / 100,
            "is_outlier": False,
            "embedding_dims": len(embedding),
            "method": "hash_fallback"
        }