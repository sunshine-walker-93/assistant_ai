"""Configuration management."""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator


class Config(BaseSettings):
    """Application configuration."""
    
    # gRPC server
    grpc_addr: str = "0.0.0.0:50051"
    
    # LLM configuration
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    openai_base_url: Optional[str] = None  # Custom base URL for local models (e.g., Ollama, LocalAI)
    openai_model: str = "gpt-3.5-turbo"  # OpenAI model name
    openai_temperature: float = 0.7  # Model temperature
    
    # Agent configuration
    default_agent: Optional[str] = None
    enable_orchestration: bool = False
    
    # Logging
    log_level: str = "INFO"
    
    @field_validator('openai_api_key', 'anthropic_api_key', 'openai_base_url', mode='before')
    @classmethod
    def normalize_empty_string(cls, v):
        """Convert empty strings to None."""
        if v == "" or (isinstance(v, str) and v.strip() == ""):
            return None
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


def load_config() -> Config:
    """Load configuration from environment."""
    return Config()

