# backend/config.py
import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class Config:
    """Central configuration for the entire system"""
    
    # ─── Redis Configuration ───
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    REDIS_MAX_MEMORY: str = "512mb"
    
    # ─── Database Configuration ───
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://feedback:feedback123@localhost:5432/feedback_db"
    )
    
    # ─── Azure OpenAI Configuration ───
    AZURE_OPENAI_KEY: Optional[str] = os.getenv("AZURE_OPENAI_KEY")
    AZURE_OPENAI_ENDPOINT: Optional[str] = os.getenv("AZURE_OPENAI_ENDPOINT")
    GPT_MODEL: str = "gpt-4o-mini"
    GPT_MAX_TOKENS: int = 300
    GPT_TEMPERATURE: float = 0.7
    
    # ─── HuggingFace Configuration ───
    HF_TOKEN: Optional[str] = os.getenv("HF_TOKEN")
    
    # ─── Model Configuration ───
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    SENTIMENT_MODEL: str = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    EMBEDDING_DIMENSION: int = 384
    
    # ─── Queue Names ───
    QUEUE_RAW_FEEDBACK: str = "queue:feedback:raw"
    QUEUE_PREPROCESSED: str = "queue:feedback:preprocessed"
    QUEUE_EMBEDDED: str = "queue:feedback:embedded"
    QUEUE_SENTIMENT: str = "queue:feedback:sentiment"
    QUEUE_THEMES: str = "queue:feedback:themes"
    QUEUE_BIAS_CHECK: str = "queue:feedback:bias_check"
    QUEUE_RECOMMENDATION: str = "queue:feedback:recommendation"
    QUEUE_COMPLETED: str = "queue:feedback:completed"
    QUEUE_FAILED: str = "queue:feedback:failed"
    
    # ─── Processing Configuration ───
    EMBEDDING_BATCH_SIZE: int = 32
    SENTIMENT_BATCH_SIZE: int = 16
    MAX_TEXT_LENGTH: int = 512
    MIN_TEXT_LENGTH: int = 10
    
    # ─── Bias Detection Configuration ───
    BIAS_CONFIDENCE_THRESHOLD: float = 0.7
    MAX_BIAS_SEVERITY_FOR_AUTO: float = 0.6
    
    # ─── Theme Extraction Configuration ───
    MIN_TOPIC_SIZE: int = 5
    RECLUSTERING_INTERVAL_HOURS: int = 24
    UMAP_N_NEIGHBORS: int = 15
    UMAP_N_COMPONENTS: int = 5
    
    # ─── Job Configuration ───
    JOB_TIMEOUT_SECONDS: int = 300
    STATUS_POLL_INTERVAL: int = 2
    
    # ─── Monitoring Configuration ───
    ENABLE_METRICS: bool = True
    LOG_LEVEL: str = "INFO"

config = Config()