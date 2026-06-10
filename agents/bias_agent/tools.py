# agents/bias_agent/tools.py
from agents.bias_agent.fairness_rules import FairnessRules, BiasType
from typing import Dict, List, Tuple

class PatternDetector:
    """Tool: Detects bias patterns in text"""
    
    @staticmethod
    def detect(text: str) -> List[Dict]:
        text_lower = text.lower()
        detected = []
        
        for bias_type, patterns in FairnessRules.get_all_patterns().items():
            flagged = [ind for ind in patterns["indicators"] if ind.lower() in text_lower]
            if flagged:
                severity = min(1.0, len(flagged) * patterns["weight"] / 5)
                detected.append({
                    "type": bias_type,
                    "severity": severity,
                    "terms": flagged,
                    "explanation": patterns["explanation"]
                })
        
        return detected

class ContextAnalyzer:
    """Tool: Analyzes context to distinguish reporting from direct bias"""
    
    @staticmethod
    def is_reporting(text: str, bias_terms: List[str]) -> bool:
        for term in bias_terms:
            idx = text.find(term)
            if idx > 0:
                context = text[max(0, idx-50):idx]
                if any(phrase in context for phrase in FairnessRules.REPORTING_PHRASES):
                    return True
        return False
    
    @staticmethod
    def assess_educational_value(text: str, bias: Dict) -> Tuple[bool, str]:
        if not bias or bias["severity"] < 0.6:
            return True, "Has educational value"
        
        cleaned = text
        for term in bias.get("terms", []):
            cleaned = cleaned.replace(term, "")
        
        remaining = len(cleaned.strip().split())
        if remaining < 5:
            return False, "Primarily biased statements with no constructive content"
        
        return True, f"Has {remaining} substantive words beyond bias"