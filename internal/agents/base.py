"""Base Agent class for all AI agents."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel


class AgentMetadata(BaseModel):
    """Metadata about an agent."""
    name: str
    description: str
    capabilities: list[str] = []
    is_active: bool = True


class BaseAgent(ABC):
    """Base class for all AI agents."""
    
    def __init__(self, metadata: AgentMetadata):
        self.metadata = metadata
    
    @abstractmethod
    async def process(self, message: str, context: Dict[str, Any] = None) -> str:
        """
        Process a user message and return a response.
        
        Args:
            message: User message/query
            context: Additional context information
            
        Returns:
            Agent response text
        """
        pass
    
    @abstractmethod
    async def process_stream(self, message: str, context: Dict[str, Any] = None):
        """
        Process a user message and yield streaming responses.
        
        Args:
            message: User message/query
            context: Additional context information
            
        Yields:
            Response chunks
        """
        pass
    
    def get_metadata(self) -> AgentMetadata:
        """Get agent metadata."""
        return self.metadata
    
    def is_available(self) -> bool:
        """Check if agent is available."""
        return self.metadata.is_active

