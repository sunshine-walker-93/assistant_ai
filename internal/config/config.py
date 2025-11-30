"""Configuration management."""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    """Application configuration."""
    
    # gRPC server
    grpc_addr: str = "0.0.0.0:50052"
    
    # LLM configuration
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # Agent configuration
    default_agent: Optional[str] = None
    enable_orchestration: bool = False
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


def load_config() -> Config:
    """Load configuration from environment."""
    return Config()

