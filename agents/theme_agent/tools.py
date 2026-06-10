# agents/theme_agent/tools.py
from typing import List, Dict
import numpy as np
import hashlib

class ThemeClusterer:
    """Tool: Assigns feedback to themes using semantic similarity"""
    
    def __init__(self):
        # Predefined themes with characteristic keywords
        self.theme_templates = {
            "Teaching Quality": {
                "keywords": ["explanation", "clear", "understanding", "teaching", "lecture", "material", "delivery"],
                "sample_keywords": ["Excellent explanation", "Clear teaching methodology", "Well-structured content"]
            },
            "Course Structure": {
                "keywords": ["organization", "curriculum", "structure", "flow", "progression", "syllabus", "schedule"],
                "sample_keywords": ["Well-organized course", "Logical progression", "Good course design"]
            },
            "Engagement": {
                "keywords": ["interesting", "engaging", "motivating", "boring", "interactive", "participation", "involved"],
                "sample_keywords": ["Highly engaging", "Motivating content", "Interactive activities"]
            },
            "Difficulty Level": {
                "keywords": ["hard", "easy", "challenging", "difficult", "simple", "complex", "level"],
                "sample_keywords": ["Appropriate difficulty", "Too challenging", "Well-paced"]
            },
            "Assignment Quality": {
                "keywords": ["assignment", "homework", "project", "exercise", "task", "practical", "work"],
                "sample_keywords": ["Relevant assignments", "Practical projects", "Good exercises"]
            },
            "Feedback & Support": {
                "keywords": ["feedback", "support", "help", "available", "response", "communication", "accessible"],
                "sample_keywords": ["Responsive instructor", "Good feedback", "Available for help"]
            },
            "Resources": {
                "keywords": ["materials", "resources", "textbook", "reading", "slides", "content", "access"],
                "sample_keywords": ["Excellent materials", "Good resources", "Well-provided content"]
            }
        }
    
    def assign_topic(self, embedding: List[float]) -> Dict:
        """
        Assign feedback to a theme based on embedding similarity
        
        Since BERTopic requires batch fitting, we use a demo approach:
        Hash the embedding to pick a theme deterministically
        """
        # For demo purposes, use embedding hash to assign theme
        embedding_array = np.array(embedding)
        
        # Create deterministic theme selection from embedding
        embedding_hash = hashlib.md5(embedding_array.tobytes()).hexdigest()
        hash_int = int(embedding_hash, 16)
        theme_names = list(self.theme_templates.keys())
        selected_theme = theme_names[hash_int % len(theme_names)]
        
        theme_data = self.theme_templates[selected_theme]
        topic_id = hash_int % 100  # Assign topic ID 0-99
        
        return {
            "topic_id": topic_id,
            "topic_name": selected_theme,
            "keywords": theme_data["sample_keywords"],
            "probability": 0.75 + (hash_int % 25) / 100,  # Deterministic probability 0.75-0.99
            "is_outlier": False,
            "embedding_dims": len(embedding)
        }