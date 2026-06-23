# memory/long_term_memory.py
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import config
from database.init_sql_models import (
    Feedback, SentimentAnalysis, ThemeAssignment, 
    BiasCheck, Recommendation, Base
)
from typing import List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class LongTermMemory:
    """Long-term memory for agents (PostgreSQL)"""
    
    def __init__(self):
        self.engine = create_engine(config.DATABASE_URL)
        Base.metadata.create_all(self.engine)
        self._migrate_sqlite()
        self.Session = sessionmaker(bind=self.engine)
        
    def _migrate_sqlite(self):
        """Auto-migrate SQLite database if columns are missing"""
        db_url = config.DATABASE_URL
        if not db_url.startswith("sqlite:///"):
            return
        
        import sqlite3
        import os
        db_file = db_url.replace("sqlite:///", "")
        if not os.path.exists(db_file):
            return
            
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            
            for table_name, table_obj in Base.metadata.tables.items():
                try:
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    existing_cols = [r[1] for r in cursor.fetchall()]
                    if not existing_cols:
                        continue
                    
                    for col_name, col_obj in table_obj.columns.items():
                        if col_name not in existing_cols:
                            col_type = "TEXT"
                            if str(col_obj.type).startswith("INTEGER"):
                                col_type = "INTEGER"
                            elif str(col_obj.type).startswith("FLOAT"):
                                col_type = "REAL"
                            elif str(col_obj.type).startswith("BOOLEAN"):
                                col_type = "INTEGER"
                            
                            alter_query = f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}"
                            cursor.execute(alter_query)
                except sqlite3.OperationalError:
                    continue
            conn.commit()
            conn.close()
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"⚠️ SQLite auto-migration failed: {e}")
    
    def save_feedback(self, data: dict):
        """Save feedback, skipping if same text_hash already exists (deduplication)"""
        session = self.Session()
        try:
            # Deduplicate by text_hash: same text content should not be re-inserted
            text_hash = data.get("text_hash")
            if text_hash:
                existing = session.query(Feedback).filter_by(text_hash=text_hash).first()
                if existing:
                    logger.debug(f"⏭️  Skipping duplicate feedback (hash={text_hash[:8]}...)")
                    return existing.id  # Return existing ID so callers can use it
            fb = Feedback(**data)
            session.add(fb)
            session.commit()
            return fb.id
        finally:
            session.close()
    
    def save_sentiment(self, data: dict):
        """Save sentiment, skipping if one already exists for this feedback_id"""
        session = self.Session()
        try:
            existing = session.query(SentimentAnalysis).filter_by(feedback_id=data["feedback_id"]).first()
            if existing:
                logger.debug(f"⏭️  Skipping duplicate sentiment for feedback {data['feedback_id'][:8]}")
                return
            sa = SentimentAnalysis(**data)
            session.add(sa)
            session.commit()
        finally:
            session.close()
    
    def save_theme(self, data: dict):
        """Save theme assignment, skipping if one already exists for this feedback_id"""
        session = self.Session()
        try:
            existing = session.query(ThemeAssignment).filter_by(feedback_id=data["feedback_id"]).first()
            if existing:
                logger.debug(f"⏭️  Skipping duplicate theme for feedback {data['feedback_id'][:8]}")
                return
            ta = ThemeAssignment(**data)
            session.add(ta)
            session.commit()
        finally:
            session.close()
    
    def save_bias_check(self, data: dict):
        """Save bias check, skipping if one already exists for this feedback_id"""
        session = self.Session()
        try:
            existing = session.query(BiasCheck).filter_by(feedback_id=data["feedback_id"]).first()
            if existing:
                logger.debug(f"⏭️  Skipping duplicate bias check for feedback {data['feedback_id'][:8]}")
                return
            bc = BiasCheck(**data)
            session.add(bc)
            session.commit()
        finally:
            session.close()
    
    def save_recommendation(self, data: dict):
        """Save recommendation, skipping if one already exists for this theme_name (unique per theme)"""
        session = self.Session()
        try:
            # Group recommendations by theme name to avoid duplicates per theme
            theme_name = data.get("theme_name", "Unknown")
            existing = session.query(Recommendation).filter_by(theme_name=theme_name, implemented=False).first()
            if existing:
                logger.debug(f"Combined recommendation already exists for theme: {theme_name}")
                return
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
                rec = session.query(Recommendation).filter_by(feedback_id=fb.id).first()
                
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
    
    def get_dashboard_summary(self) -> dict:
        """Get KPI summary for dashboard"""
        session = self.Session()
        try:
            total_feedbacks = session.query(Feedback).count()
            
            # Sentiment breakdown
            positive = session.query(SentimentAnalysis).filter_by(label="positive").count()
            negative = session.query(SentimentAnalysis).filter_by(label="negative").count()
            neutral = session.query(SentimentAnalysis).filter_by(label="neutral").count()
            
            # Recommendations by priority
            high_priority = session.query(Recommendation).filter_by(priority="high", implemented=False).count()
            medium_priority = session.query(Recommendation).filter_by(priority="medium", implemented=False).count()
            low_priority = session.query(Recommendation).filter_by(priority="low", implemented=False).count()
            
            # Bias issues
            biased_count = session.query(BiasCheck).filter_by(is_biased=True).count()
            
            # Themes
            unique_themes = session.query(ThemeAssignment).distinct(ThemeAssignment.theme_id).count()
            
            return {
                "total_feedbacks": total_feedbacks,
                "sentiment": {
                    "positive": positive,
                    "negative": negative,
                    "neutral": neutral,
                    "positive_pct": round(100 * positive / total_feedbacks, 1) if total_feedbacks > 0 else 0,
                    "negative_pct": round(100 * negative / total_feedbacks, 1) if total_feedbacks > 0 else 0,
                    "neutral_pct": round(100 * neutral / total_feedbacks, 1) if total_feedbacks > 0 else 0
                },
                "recommendations": {
                    "high_priority": high_priority,
                    "medium_priority": medium_priority,
                    "low_priority": low_priority,
                    "total_unresolved": high_priority + medium_priority + low_priority
                },
                "bias_issues": biased_count,
                "unique_themes": unique_themes
            }
        finally:
            session.close()
    
    def get_recommendations_with_meta(self) -> List[dict]:
        """Get all unresolved recommendations with full metadata"""
        session = self.Session()
        try:
            recs = session.query(Recommendation).filter_by(implemented=False).all()
            results = []
            
            for rec in recs:
                # Get theme name
                theme = session.query(ThemeAssignment).filter_by(theme_id=rec.theme_id).first()
                theme_name = rec.theme_name or (theme.theme_name if theme else "Unknown")
                
                # Get feedback text for context
                feedback = session.query(Feedback).filter_by(id=rec.feedback_id).first()
                
                results.append({
                    "id": rec.id,
                    "feedback_id": rec.feedback_id,
                    "theme_id": rec.theme_id,
                    "theme_name": theme_name,
                    "recommendation_text": rec.recommendation_text,
                    "priority": rec.priority,
                    "action_items": rec.action_items or [],
                    "expected_impact": rec.expected_impact,
                    "fairness_note": rec.fairness_note,
                    "feedback_preview": feedback.original_text[:200] if feedback else "",
                    "created_at": rec.created_at.isoformat() if rec.created_at else ""
                })
            
            return sorted(results, key=lambda x: {"high": 0, "medium": 1, "low": 2}.get(x["priority"], 3))
        finally:
            session.close()
    
    def mark_recommendation_resolved(self, rec_id: str) -> bool:
        """Mark a recommendation as implemented"""
        session = self.Session()
        try:
            rec = session.query(Recommendation).filter_by(id=rec_id).first()
            if rec:
                rec.implemented = True
                session.commit()
                return True
            return False
        finally:
            session.close()
    
    def get_chart_data(self) -> dict:
        """Get aggregated data for dashboard charts"""
        session = self.Session()
        try:
            # Theme x Sentiment matrix
            theme_sentiment = {}
            assignments = session.query(ThemeAssignment).all()
            
            for ta in assignments:
                if ta.feedback_id:
                    sentiment = session.query(SentimentAnalysis).filter_by(feedback_id=ta.feedback_id).first()
                    theme_key = ta.theme_name or f"Theme {ta.theme_id}"
                    
                    if theme_key not in theme_sentiment:
                        theme_sentiment[theme_key] = {"positive": 0, "negative": 0, "neutral": 0}
                    
                    if sentiment:
                        theme_sentiment[theme_key][sentiment.label] = theme_sentiment[theme_key].get(sentiment.label, 0) + 1
            
            # Top keywords
            all_keywords = []
            for ta in assignments:
                if ta.keywords and isinstance(ta.keywords, list):
                    all_keywords.extend(ta.keywords)
            
            keyword_counts = {}
            for kw in all_keywords:
                keyword_counts[kw] = keyword_counts.get(kw, 0) + 1
            
            top_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:15]
            
            return {
                "theme_sentiment": theme_sentiment,
                "top_keywords": [{"keyword": kw[0], "count": kw[1]} for kw in top_keywords]
            }
        finally:
            session.close()