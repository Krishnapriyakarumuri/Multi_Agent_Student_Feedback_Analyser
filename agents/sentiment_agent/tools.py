# agents/sentiment_agent/tools.py
from transformers import pipeline
from typing import Dict

class SentimentAnalyzer:
    """Tool: Analyzes sentiment using RoBERTa"""
    
    LABEL_MAP = {'LABEL_0': 'negative', 'LABEL_1': 'neutral', 'LABEL_2': 'positive'}
    
    def __init__(self):
        self.model_name = "cardiffnlp/twitter-roberta-base-sentiment-latest"
        self.pipeline = None
    
    def load_model(self):
        if self.pipeline is None:
            print(f"📦 Loading sentiment model: {self.model_name}")
            self.pipeline = pipeline("sentiment-analysis", model=self.model_name, max_length=512, truncation=True)
        return self.pipeline
    
    def analyze(self, text: str) -> Dict:
        pipe = self.load_model()
        result = pipe(text)[0]
        
        label = self.LABEL_MAP.get(result['label'], 'neutral')
        score = result['score']
        confidence = "high" if score > 0.8 else "medium" if score > 0.6 else "low"
        
        return {"label": label, "score": score, "confidence": confidence}