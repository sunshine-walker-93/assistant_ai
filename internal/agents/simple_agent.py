"""Simple example agent implementation."""

import logging
from typing import Dict, Any
from .base import BaseAgent, AgentMetadata

logger = logging.getLogger(__name__)


class SimpleAgent(BaseAgent):
    """Simple example agent that echoes user input."""
    
    def __init__(self):
        metadata = AgentMetadata(
            name="simple",
            description="A simple echo agent for testing",
            capabilities=["echo", "test"],
            is_active=True  # 显式设置为 True，确保默认 agent 是激活的
        )
        super().__init__(metadata)
    
    async def process(self, message: str, context: Dict[str, Any] = None) -> str:
        """Process message and return echo response."""
        logger.info(f"SimpleAgent processing: {message}")
        return f"Echo: {message}"
    
    async def process_stream(self, message: str, context: Dict[str, Any] = None):
        """Process message with streaming response."""
        words = message.split()
        for word in words:
            yield f"{word} "
        yield "\n"

