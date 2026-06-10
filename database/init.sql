-- database/init.sql

CREATE TABLE IF NOT EXISTS feedback (
    id VARCHAR(36) PRIMARY KEY,
    job_id VARCHAR(36),
    original_text TEXT,
    cleaned_text TEXT,
    text_hash VARCHAR(64),
    is_valid BOOLEAN DEFAULT TRUE,
    metadata JSONB DEFAULT '{}',
    processed_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sentiment_analysis (
    id VARCHAR(36) PRIMARY KEY,
    feedback_id VARCHAR(36) REFERENCES feedback(id),
    label VARCHAR(20),
    score FLOAT,
    confidence VARCHAR(10),
    processed_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS theme_assignments (
    id VARCHAR(36) PRIMARY KEY,
    feedback_id VARCHAR(36) REFERENCES feedback(id),
    theme_id INTEGER,
    theme_name VARCHAR(200),
    keywords JSONB,
    probability FLOAT,
    is_outlier BOOLEAN DEFAULT FALSE,
    processed_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS bias_checks (
    id VARCHAR(36) PRIMARY KEY,
    feedback_id VARCHAR(36) REFERENCES feedback(id),
    is_biased BOOLEAN,
    bias_type VARCHAR(50),
    severity FLOAT,
    flagged_terms JSONB,
    explanation TEXT,
    requires_human_review BOOLEAN DEFAULT FALSE,
    has_educational_value BOOLEAN DEFAULT TRUE,
    processed_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS recommendations (
    id VARCHAR(36) PRIMARY KEY,
    theme_id INTEGER,
    recommendation_text TEXT,
    priority VARCHAR(10),
    action_items JSONB,
    expected_impact TEXT,
    fairness_note TEXT,
    implemented BOOLEAN DEFAULT FALSE,
    upstream_agents JSONB,
    processed_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_feedback_job ON feedback(job_id);
CREATE INDEX IF NOT EXISTS idx_sentiment_feedback ON sentiment_analysis(feedback_id);
CREATE INDEX IF NOT EXISTS idx_theme_feedback ON theme_assignments(feedback_id);
CREATE INDEX IF NOT EXISTS idx_theme_id ON theme_assignments(theme_id);
CREATE INDEX IF NOT EXISTS idx_bias_feedback ON bias_checks(feedback_id);
CREATE INDEX IF NOT EXISTS idx_rec_theme ON recommendations(theme_id);