# agents/preprocessing_agent/agent.py
from agents.base_agent import BaseAgent, AgentThought
from typing import Dict, Any
import re
import hashlib
import unicodedata

class PreprocessingAgent(BaseAgent):
    """
    Agent responsible for cleaning and preparing feedback text.
    
    Role: Data Preparation Specialist
    Tools: TextNormalizer, DuplicateDetector, LanguageIdentifier
    """
    
    def __init__(self):
        super().__init__(
            name="Preprocessing Agent",
            role="Data Preparation & Cleaning",
            tools=["text_normalizer", "duplicate_detector", "language_identifier"]
        )
    
    @property
    def system_prompt(self) -> str:
        return """
        You are the Preprocessing Agent, the first agent in our multi-agent 
        feedback analysis system. Your mission is to:
        
        1. Clean raw student feedback text
        2. Remove noise, special characters, and inconsistencies
        3. Detect and flag duplicate feedback
        4. Identify the language of feedback
        5. Prepare clean, structured data for downstream agents
        
        You are the foundation of our analysis pipeline. 
        Clean input = Quality insights.
        """
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute preprocessing on feedback text
        """
        text = task.get("text", "")
        feedback_id = task.get("feedback_id", "unknown")
        
        # Step 1: Think about the text
        self.think(
            thought=f"Received feedback [{feedback_id}] with {len(text)} characters",
            action="analyze_text",
            observation=f"Text length: {len(text)}"
        )
        
        # Step 2: Clean the text
        self.think(
            thought="Normalizing text - removing noise and standardizing format",
            action="clean_text",
            observation=""
        )
        
        cleaned_text = self._clean_text(text)
        
        # Step 3: Check for duplicates
        text_hash = self._generate_hash(cleaned_text)
        self.think(
            thought=f"Generated text hash: {text_hash[:16]}...",
            action="hash_text",
            observation="Hash created for deduplication"
        )
        
        # Step 4: Detect language
        language = self._detect_language(cleaned_text)
        self.think(
            thought=f"Detected language: {language}",
            action="detect_language",
            observation=f"Language: {language}"
        )
        
        # Step 5: Validate
        word_count = len(cleaned_text.split())
        is_valid = 10 <= len(cleaned_text) <= 512
        
        self.think(
            thought=f"Validation complete. Words: {word_count}, Valid: {is_valid}",
            action="validate",
            observation="Ready for downstream agents"
        )
        
        return {
            "feedback_id": feedback_id,
            "original_text": text,
            "cleaned_text": cleaned_text,
            "text_hash": text_hash,
            "word_count": word_count,
            "language": language,
            "is_valid": is_valid,
            "processed_by": self.name,
            "agent_id": self.agent_id
        }
    
    def _clean_text(self, text: str) -> str:
        """Tool: Text Normalizer"""
        text = text.strip()
        text = unicodedata.normalize('NFKD', text)
        text = re.sub(r'[^\w\s.,!?;:\-\'\"()]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.lower()
    
    def _generate_hash(self, text: str) -> str:
        """Tool: Duplicate Detector"""
        return hashlib.md5(text.encode()).hexdigest()
    
    def _detect_language(self, text: str) -> str:
        """Tool: Language Identifier"""
        english_words = {'the', 'is', 'are', 'was', 'were', 'and', 'but', 'or', 'not', 'this'}
        words = set(text.split())
        english_count = len(words & english_words)
        return "en" if english_count >= 2 else "unknown"