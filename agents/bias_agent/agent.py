# agents/bias_agent/agent.py
from agents.base_agent import BaseAgent
from typing import Dict, Any, List
from enum import Enum

class BiasType(Enum):
    GENDER = "gender_bias"
    RACIAL = "racial_bias"
    AGE = "age_bias"
    DISABILITY = "disability_bias"
    SOCIOECONOMIC = "socioeconomic_bias"
    NONE = "no_bias"

class BiasDetectionAgent(BaseAgent):
    """
    Agent responsible for ensuring fairness in feedback analysis.
    
    Role: Fairness Guardian
    Tools: PatternDetector, ContextAnalyzer, FairnessValidator
    """
    
    def __init__(self):
        super().__init__(
            name="Bias Detection Agent",
            role="Fairness & Bias Detection",
            tools=["pattern_detector", "context_analyzer", "fairness_validator"]
        )
        self._initialize_fairness_knowledge()
    
    @property
    def system_prompt(self) -> str:
        return """
        You are the Bias Detection Agent, the ethical guardian of our 
        multi-agent feedback analysis system. Your mission is to:
        
        1. Detect biased language in student feedback
        2. Distinguish between legitimate criticism and prejudiced statements
        3. Protect downstream agents from amplifying bias
        4. Ensure recommendations are fair and inclusive
        5. Flag content requiring human review
        
        Core Principle: Address legitimate concerns WITHOUT validating prejudice.
        You are the conscience of our AI system.
        """
    
    def _initialize_fairness_knowledge(self):
        """Load the agent's fairness knowledge base"""
        self.fairness_patterns = {
            BiasType.GENDER: {
                "indicators": [
                    "male students are better", "female students can't",
                    "boys naturally", "girls should", "like a girl", "man up"
                ],
                "weight": 0.8,
                "explanation": "Gender-based stereotyping detected"
            },
            BiasType.RACIAL: {
                "indicators": [
                    "they always", "those people", "their kind",
                    "because of their background", "due to their community"
                ],
                "weight": 0.9,
                "explanation": "Racial/ethnic generalization detected"
            },
            BiasType.AGE: {
                "indicators": [
                    "too old to learn", "too young to understand",
                    "boomers", "gen z is lazy", "kids these days"
                ],
                "weight": 0.6,
                "explanation": "Age-based stereotyping detected"
            },
            BiasType.DISABILITY: {
                "indicators": [
                    "handicapped", "retarded", "mentally slow",
                    "can't keep up because of", "special needs kids"
                ],
                "weight": 0.9,
                "explanation": "Ableist language detected"
            },
            BiasType.SOCIOECONOMIC: {
                "indicators": [
                    "poor people can't", "rich kids always",
                    "scholarship students are", "because they're poor"
                ],
                "weight": 0.7,
                "explanation": "Socioeconomic stereotyping detected"
            }
        }
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze feedback for bias before recommendations
        """
        text = task.get("cleaned_text", "")
        sentiment = task.get("sentiment", {})
        theme = task.get("theme", {})
        feedback_id = task.get("feedback_id", "unknown")
        
        # Step 1: Scan for bias patterns
        self.think(
            thought=f"Scanning feedback [{feedback_id}] for bias indicators",
            action="scan_patterns",
            observation=""
        )
        
        detected_biases = self._scan_for_bias(text)
        
        # Step 2: Analyze context
        self.think(
            thought=f"Found {len(detected_biases)} potential bias indicators",
            action="analyze_context",
            observation=f"Bias types: {[b['type'].value for b in detected_biases]}"
        )
        
        if detected_biases:
            # Determine if bias is contextual or direct
            for bias in detected_biases:
                is_contextual = self._is_reporting_bias(text, bias)
                bias["is_contextual"] = is_contextual
                
                self.think(
                    thought=f"Analyzing: {bias['type'].value} - Contextual: {is_contextual}",
                    action="context_analysis",
                    observation=f"Severity adjusted based on context"
                )
        
        # Step 3: Generate fairness guardrails
        primary_bias = max(detected_biases, key=lambda x: x["severity"]) if detected_biases else None
        
        if primary_bias:
            self.think(
                thought=f"Primary bias: {primary_bias['type'].value} (severity: {primary_bias['severity']:.2f})",
                action="generate_guardrails",
                observation="Creating bias context for downstream agents"
            )
        
        # Step 4: Generate guardrails for Recommendation Agent
        bias_guardrails = self._generate_guardrails(primary_bias, text)
        
        # Step 5: Check if feedback has educational value
        has_value, reason = self._assess_educational_value(text, primary_bias)
        
        self.think(
            thought=f"Educational value assessment: {'Valid' if has_value else 'Filtered'} - {reason}",
            action="value_assessment",
            observation=reason
        )
        
        return {
            "feedback_id": feedback_id,
            "is_biased": primary_bias is not None and not (primary_bias.get("is_contextual") and primary_bias["severity"] < 0.5),
            "bias_type": primary_bias["type"].value if primary_bias else "none",
            "severity": primary_bias["severity"] if primary_bias else 0.0,
            "detected_indicators": primary_bias["terms"][:5] if primary_bias else [],
            "explanation": primary_bias["explanation"] if primary_bias else "No bias detected",
            "guardrails_for_recommendation": bias_guardrails,
            "has_educational_value": has_value,
            "value_assessment_reason": reason,
            "requires_human_review": primary_bias["severity"] > 0.7 if primary_bias else False,
            "processed_by": self.name,
            "agent_id": self.agent_id
        }
    
    def _scan_for_bias(self, text: str) -> List[Dict]:
        """Tool: Pattern Detector"""
        text_lower = text.lower()
        detected = []
        
        for bias_type, patterns in self.fairness_patterns.items():
            flagged = []
            for indicator in patterns["indicators"]:
                if indicator.lower() in text_lower:
                    flagged.append(indicator)
            
            if flagged:
                severity = min(1.0, len(flagged) * patterns["weight"] / 5)
                detected.append({
                    "type": bias_type,
                    "severity": severity,
                    "terms": flagged,
                    "explanation": patterns["explanation"]
                })
        
        return detected
    
    def _is_reporting_bias(self, text: str, bias: Dict) -> bool:
        """Tool: Context Analyzer - Check if person is reporting someone else's bias"""
        reporting_phrases = [
            "said that", "mentioned that", "told us", "according to",
            "they say", "people say", "heard that", "reported that"
        ]
        
        for term in bias.get("terms", []):
            term_index = text.find(term)
            if term_index > 0:
                context_before = text[max(0, term_index-50):term_index]
                if any(phrase in context_before for phrase in reporting_phrases):
                    return True
        return False
    
    def _generate_guardrails(self, bias: Dict, text: str) -> str:
        """Generate guardrails for the Recommendation Agent"""
        if not bias:
            return ""
        
        return f"""
        ⚠️ BIAS ALERT FOR RECOMMENDATION AGENT:
        
        Type: {bias['type'].value}
        Severity: {bias['severity']:.2f}/1.0
        Context: {bias.get('is_contextual', False)}
        
        GUIDELINES:
        1. Do NOT amplify or validate the biased perspective
        2. Address legitimate underlying concerns without endorsing stereotypes
        3. Frame all recommendations in inclusive, equitable language
        4. Focus on systemic improvements, not group characteristics
        5. If no legitimate concern exists behind the bias, note for human review
        
        Original text excerpt: "{text[:200]}..."
        """
    
    def _assess_educational_value(self, text: str, bias: Dict) -> tuple:
        """Check if feedback has educational value beyond bias"""
        if not bias or bias["severity"] < 0.6:
            return True, "Feedback has educational value"
        
        # Remove biased terms and check remaining content
        cleaned = text
        for term in bias.get("terms", []):
            cleaned = cleaned.replace(term, "")
        
        remaining_words = len(cleaned.strip().split())
        
        if remaining_words < 5:
            return False, "Feedback consists primarily of biased statements"
        
        return True, f"Feedback has {remaining_words} substantive words after bias removal"