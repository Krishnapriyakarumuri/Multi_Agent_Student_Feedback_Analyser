# agents/preprocessing_agent/tools.py
import re
import hashlib
import unicodedata
from typing import Dict, Any, Tuple

class TextCleaner:
    """Tool: Cleans and normalizes text"""
    
    @staticmethod
    def clean(text: str) -> str:
        text = text.strip()
        text = unicodedata.normalize('NFKD', text)
        text = re.sub(r'[^\w\s.,!?;:\-\'\"()]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.lower()

class DuplicateDetector:
    """Tool: Detects duplicate feedback"""
    
    @staticmethod
    def generate_hash(text: str) -> str:
        return hashlib.md5(text.encode()).hexdigest()

class LanguageIdentifier:
    """Tool: Identifies language of feedback"""
    
    ENGLISH_INDICATORS = {'the', 'is', 'are', 'was', 'were', 'and', 'but', 'or', 'not', 'this', 'that'}
    
    @classmethod
    def detect(cls, text: str) -> str:
        words = set(text.split())
        english_count = len(words & cls.ENGLISH_INDICATORS)
        return "en" if english_count >= 2 else "unknown"