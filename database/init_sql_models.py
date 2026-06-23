# database/init_sql_models.py
from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime, JSON, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(String(36), primary_key=True, default=lambda: str(__import__('uuid').uuid4()))
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    role = Column(String(20), default="viewer")  # admin or viewer
    created_at = Column(DateTime, default=datetime.now)

class Feedback(Base):
    __tablename__ = "feedback"
    id = Column(String(36), primary_key=True)
    job_id = Column(String(36))
    original_text = Column(Text)
    cleaned_text = Column(Text)
    text_hash = Column(String(64))
    is_valid = Column(Boolean, default=True)
    processed_by = Column(String(100))
    created_at = Column(DateTime, default=datetime.now)

class SentimentAnalysis(Base):
    __tablename__ = "sentiment_analysis"
    id = Column(String(36), primary_key=True, default=lambda: str(__import__('uuid').uuid4()))
    feedback_id = Column(String(36))
    label = Column(String(20))
    score = Column(Float)
    confidence = Column(String(10))
    processed_by = Column(String(100))
    created_at = Column(DateTime, default=datetime.now)

class ThemeAssignment(Base):
    __tablename__ = "theme_assignments"
    id = Column(String(36), primary_key=True, default=lambda: str(__import__('uuid').uuid4()))
    feedback_id = Column(String(36))
    theme_id = Column(Integer)
    theme_name = Column(String(200))
    keywords = Column(JSON)
    probability = Column(Float)
    is_outlier = Column(Boolean, default=False)
    processed_by = Column(String(100))
    created_at = Column(DateTime, default=datetime.now)

class BiasCheck(Base):
    __tablename__ = "bias_checks"
    id = Column(String(36), primary_key=True, default=lambda: str(__import__('uuid').uuid4()))
    feedback_id = Column(String(36))
    is_biased = Column(Boolean)
    bias_type = Column(String(50))
    severity = Column(Float)
    flagged_terms = Column(JSON)
    explanation = Column(Text)
    reliability_score = Column(Float, default=1.0)
    is_anomaly = Column(Boolean, default=False)
    requires_human_review = Column(Boolean, default=False)
    has_educational_value = Column(Boolean, default=True)
    processed_by = Column(String(100))
    created_at = Column(DateTime, default=datetime.now)

class Recommendation(Base):
    __tablename__ = "recommendations"
    id = Column(String(36), primary_key=True, default=lambda: str(__import__('uuid').uuid4()))
    feedback_id = Column(String(36))
    theme_id = Column(Integer)
    theme_name = Column(String(200))
    recommendation_text = Column(Text)
    priority = Column(String(10))
    action_items = Column(JSON)
    expected_impact = Column(Text)
    fairness_note = Column(Text)
    implemented = Column(Boolean, default=False)
    upstream_agents = Column(JSON)
    processed_by = Column(String(100))
    created_at = Column(DateTime, default=datetime.now)