# agents/embedding_agent/__init__.py
from .agent import EmbeddingAgent
from .tools import EmbeddingGenerator
from .prompt import EMBEDDING_SYSTEM_PROMPT

__all__ = ['EmbeddingAgent', 'EmbeddingGenerator']