# config.py
import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class Config:
    """Hackathon Config - No Redis, No PostgreSQL"""
    
    # Use SQLite
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///feedback_analysis.db")
    
    # Use in-memory (no Redis)
    REDIS_URL: str = os.getenv("REDIS_URL", "memory://")
    
    # Azure OpenAI
    AZURE_OPENAI_KEY: Optional[str] = os.getenv("AZURE_OPENAI_KEY", "demo-key")
    AZURE_OPENAI_ENDPOINT: Optional[str] = os.getenv("AZURE_OPENAI_ENDPOINT", "https://demo.openai.azure.com/")
    GPT_MODEL: str = "gpt-4o-mini"

    # Groq (recommendations + theme label generation)
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = "llama-3.1-8b-instant"   # fast & capable; change to llama-3.3-70b-versatile for richer output
    GPT_MAX_TOKENS: int = 300
    GPT_TEMPERATURE: float = 0.7
    
    # Models
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    SENTIMENT_MODEL: str = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    
    # Processing
    MAX_TEXT_LENGTH: int = 512
    MIN_TEXT_LENGTH: int = 10
    BIAS_SEVERITY_THRESHOLD: float = 0.7
    MIN_TOPIC_SIZE: int = 5
    
    # Logging
    LOG_LEVEL: str = "INFO"

config = Config()