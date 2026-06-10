# api/schemas.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum

class SentimentLabel(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"

class Priority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class BiasType(str, Enum):
    GENDER = "gender_bias"
    RACIAL = "racial_bias"
    AGE = "age_bias"
    DISABILITY = "disability_bias"
    SOCIOECONOMIC = "socioeconomic_bias"
    NONE = "no_bias"

class UploadResponse(BaseModel):
    job_id: str
    total_feedbacks: int
    message: str
    agents_involved: List[str]
    status_check_url: str

class AgentInfo(BaseModel):
    name: str
    role: str
    status: str
    tools: List[str]
    messages_processed: int

class TaskStatus(BaseModel):
    task_id: str
    status: str
    progress: float
    current_agent: str
    completed_agents: List[str]
    pending_agents: List[str]

class SentimentResult(BaseModel):
    label: SentimentLabel
    score: float
    confidence: str
    processed_by: str

class ThemeResult(BaseModel):
    theme_id: int
    theme_name: str
    keywords: List[str]
    probability: float
    processed_by: str

class BiasResult(BaseModel):
    is_biased: bool
    bias_type: BiasType
    severity: float
    explanation: str
    requires_human_review: bool
    processed_by: str

class RecommendationResult(BaseModel):
    recommendation_text: str
    priority: Priority
    action_items: List[str]
    expected_impact: str
    fairness_note: Optional[str]
    upstream_agents: List[str]
    processed_by: str

class AnalysisResult(BaseModel):
    feedback_id: str
    original_text: str
    cleaned_text: str
    sentiment: SentimentResult
    theme: ThemeResult
    bias_check: BiasResult
    recommendation: RecommendationResult
    processed_at: datetime
    agents_chain: List[str]

class AgentDashboardData(BaseModel):
    total_agents: int
    agents_online: int
    tasks_completed: int
    tasks_pending: int
    agent_details: List[AgentInfo]