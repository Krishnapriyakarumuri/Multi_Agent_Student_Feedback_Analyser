# agents/embedding_agent/tools.py
from sentence_transformers import SentenceTransformer
from typing import List
from config import config

class EmbeddingGenerator:
    """Tool: Generates semantic embeddings"""
    
    def __init__(self):
        self.model_name = config.EMBEDDING_MODEL
        self.model = None
    
    def load_model(self):
        if self.model is None:
            print(f"📦 Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
        return self.model
    
    def generate(self, text: str) -> List[float]:
        model = self.load_model()
        embedding = model.encode(text, normalize_embeddings=True)
        return embedding.tolist()