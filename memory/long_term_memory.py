# memory/long_term_memory.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import config
from database.init_sql_models import (
    Feedback, SentimentAnalysis, ThemeAssignment, 
    BiasCheck, Recommendation, Base
)
from typing import List, Optional
from datetime import datetime

class LongTermMemory:
    """Long-term memory for agents (PostgreSQL)"""
    
    def __init__(self):
        self.engine = create_engine(config.DATABASE_URL)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
    
    def save_feedback(self, data: dict):
        session = self.Session()
        try:
            fb = Feedback(**data)
            session.add(fb)
            session.commit()
        finally:
            session.close()
    
    def save_sentiment(self, data: dict):
        session = self.Session()
        try:
            sa = SentimentAnalysis(**data)
            session.add(sa)
            session.commit()
        finally:
            session.close()
    
    def save_theme(self, data: dict):
        session = self.Session()
        try:
            ta = ThemeAssignment(**data)
            session.add(ta)
            session.commit()
        finally:
            session.close()
    
    def save_bias_check(self, data: dict):
        session = self.Session()
        try:
            bc = BiasCheck(**data)
            session.add(bc)
            session.commit()
        finally:
            session.close()
    
    def save_recommendation(self, data: dict):
        session = self.Session()
        try:
            rec = Recommendation(**data)
            session.add(rec)
            session.commit()
        finally:
            session.close()
    
    def get_analysis_results(self, job_id: str) -> List[dict]:
        session = self.Session()
        try:
            feedbacks = session.query(Feedback).filter_by(job_id=job_id).all()
            results = []
            for fb in feedbacks:
                sentiment = session.query(SentimentAnalysis).filter_by(feedback_id=fb.id).first()
                theme = session.query(ThemeAssignment).filter_by(feedback_id=fb.id).first()
                bias = session.query(BiasCheck).filter_by(feedback_id=fb.id).first()
                rec = session.query(Recommendation).filter_by(id=fb.id).first()
                
                results.append({
                    "feedback_id": fb.id,
                    "original_text": fb.original_text,
                    "cleaned_text": fb.cleaned_text,
                    "sentiment": {"label": sentiment.label, "score": sentiment.score} if sentiment else {},
                    "theme": {"theme_id": theme.theme_id, "keywords": theme.keywords} if theme else {},
                    "bias_check": {"is_biased": bias.is_biased, "bias_type": bias.bias_type} if bias else {},
                    "recommendation": {"recommendation_text": rec.recommendation_text, "priority": rec.priority} if rec else {},
                    "processed_at": datetime.now().isoformat()
                })
            return results
        finally:
            session.close()
    
    def get_current_themes(self) -> dict:
        session = self.Session()
        try:
            themes = session.query(ThemeAssignment).limit(50).all()
            return {"themes": [{"theme_id": t.theme_id, "keywords": t.keywords} for t in themes]}
        finally:
            session.close()
    
    def get_bias_report(self) -> dict:
        session = self.Session()
        try:
            biased = session.query(BiasCheck).filter_by(is_biased=True).all()
            return {"total_biased": len(biased), "details": [{"bias_type": b.bias_type, "severity": b.severity} for b in biased]}
        finally:
            session.close()
    
    def get_active_recommendations(self) -> dict:
        session = self.Session()
        try:
            recs = session.query(Recommendation).filter_by(implemented=False).limit(20).all()
            return {"recommendations": [{"text": r.recommendation_text, "priority": r.priority, "actions": r.action_items} for r in recs]}
        finally:
            session.close()