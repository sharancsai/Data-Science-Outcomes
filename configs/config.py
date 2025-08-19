"""
AWS Learning Agent Configuration Module

This module handles all configuration settings for the AWS learning agent,
including model configurations, database settings, and deployment options.
"""

import os
from pathlib import Path
from typing import Optional
from pydantic import BaseSettings, Field

class AgentConfig(BaseSettings):
    """Configuration settings for the AWS learning agent."""
    
    # Model Configuration
    model_type: str = Field(default="ollama", description="Model type: ollama or huggingface")
    model_name: str = Field(default="llama3.2", description="Name of the model to use")
    
    # Ollama Configuration
    ollama_base_url: str = Field(default="http://localhost:11434", description="Ollama API base URL")
    
    # Hugging Face Configuration
    huggingface_api_key: Optional[str] = Field(default=None, description="Hugging Face API key")
    huggingface_model_name: str = Field(default="microsoft/DialoGPT-medium", description="HF model name")
    
    # Database Configuration
    database_url: str = Field(default="sqlite:///./aws_agent.db", description="Database connection URL")
    
    # Agent Configuration
    agent_name: str = Field(default="AWS Learning Assistant", description="Name of the agent")
    max_memory_size: int = Field(default=1000, description="Maximum number of memory entries to retain")
    feedback_enabled: bool = Field(default=True, description="Enable feedback collection")
    
    # AWS Learning Content
    aws_content_path: str = Field(default="./data/aws_content", description="Path to AWS learning content")
    knowledge_base_path: str = Field(default="./data/knowledge_base", description="Path to knowledge base")
    
    # Deployment Configuration
    environment: str = Field(default="development", description="Deployment environment")
    port: int = Field(default=8000, description="Server port")
    host: str = Field(default="0.0.0.0", description="Server host")
    
    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: str = Field(default="./logs/agent.log", description="Log file path")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# Global configuration instance
config = AgentConfig()

def get_config() -> AgentConfig:
    """Get the global configuration instance."""
    return config

def setup_directories():
    """Create necessary directories if they don't exist."""
    directories = [
        Path(config.aws_content_path),
        Path(config.knowledge_base_path),
        Path(config.log_file).parent,
        Path("./data/feedback"),
        Path("./data/memory")
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)