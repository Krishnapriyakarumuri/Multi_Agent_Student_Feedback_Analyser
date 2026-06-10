# agents/bias_agent/fairness_rules.py
from enum import Enum

class BiasType(Enum):
    GENDER = "gender_bias"
    RACIAL = "racial_bias"
    AGE = "age_bias"
    DISABILITY = "disability_bias"
    SOCIOECONOMIC = "socioeconomic_bias"
    NONE = "no_bias"

class FairnessRules:
    """Defines fairness patterns and rules for bias detection"""
    
    PATTERNS = {
        BiasType.GENDER: {
            "indicators": ["male students are better", "female students can't", "boys naturally", "girls should", "like a girl", "man up", "women don't belong", "men are more suited"],
            "weight": 0.8,
            "explanation": "Gender-based stereotyping detected"
        },
        BiasType.RACIAL: {
            "indicators": ["they always", "those people", "their kind", "because of their background", "due to their community", "as expected from"],
            "weight": 0.9,
            "explanation": "Racial/ethnic generalization detected"
        },
        BiasType.AGE: {
            "indicators": ["too old to learn", "too young to understand", "boomers", "gen z is lazy", "kids these days", "at their age"],
            "weight": 0.6,
            "explanation": "Age-based stereotyping detected"
        },
        BiasType.DISABILITY: {
            "indicators": ["handicapped", "retarded", "mentally slow", "can't keep up because of", "special needs kids", "physically incapable"],
            "weight": 0.9,
            "explanation": "Ableist language detected"
        },
        BiasType.SOCIOECONOMIC: {
            "indicators": ["poor people can't", "rich kids always", "scholarship students are", "because they're poor", "privileged background"],
            "weight": 0.7,
            "explanation": "Socioeconomic stereotyping detected"
        }
    }
    
    REPORTING_PHRASES = ["said that", "mentioned that", "told us", "according to", "they say", "people say", "heard that", "reported that"]
    
    @classmethod
    def get_all_patterns(cls):
        return cls.PATTERNS