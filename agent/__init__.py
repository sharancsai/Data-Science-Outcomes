"""
AWS Agentic Learning Agent Package

This package provides a complete agentic agent implementation for AWS learner lab integration.
It includes the core agent, memory management, feedback collection, and knowledge base components.
"""

from .core_agent import AWSLearningAgent
from .memory_manager import MemoryManager
from .feedback_collector import FeedbackCollector  
from .knowledge_base import AWSKnowledgeBase

__version__ = "1.0.0"
__author__ = "AWS Learning Agent Team"

__all__ = [
    "AWSLearningAgent",
    "MemoryManager", 
    "FeedbackCollector",
    "AWSKnowledgeBase"
]