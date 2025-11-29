"""Router for selecting appropriate agent based on request."""

from typing import Optional, Dict, Any
import logging
from .base import BaseAgent
from .registry import AgentRegistry

logger = logging.getLogger(__name__)


class AgentRouter:
    """Router for selecting agents based on routing strategy."""
    
    def __init__(self, registry: AgentRegistry):
        self.registry = registry
    
    async def route(
        self, 
        message: str, 
        context: Dict[str, Any] = None,
        explicit_agent: Optional[str] = None
    ) -> Optional[BaseAgent]:
        """
        Route a message to an appropriate agent.
        
        Args:
            message: User message
            context: Additional context
            explicit_agent: Explicitly specified agent name (optional)
            
        Returns:
            Selected agent or None if no suitable agent found
        """
        # If agent is explicitly specified, use it
        if explicit_agent:
            agent = self.registry.get(explicit_agent)
            if agent and agent.is_available():
                logger.info(f"Routing to explicitly specified agent: {explicit_agent}")
                return agent
            else:
                logger.warning(f"Explicitly specified agent '{explicit_agent}' not found or unavailable")
        
        # Simple routing strategy: use default agent for now
        # TODO: Implement semantic routing or rule-based routing
        agent = self.registry.get_default_agent()
        if agent:
            logger.info(f"Routing to default agent: {agent.metadata.name}")
            return agent
        
        logger.error("No available agent found")
        return None
    
    async def route_semantic(
        self,
        message: str,
        context: Dict[str, Any] = None
    ) -> Optional[BaseAgent]:
        """
        Route using semantic similarity (to be implemented).
        
        This would use embeddings to find the most suitable agent
        based on the message content and agent capabilities.
        
        Args:
            message: User message
            context: Additional context
            
        Returns:
            Selected agent or None
        """
        # TODO: Implement semantic routing using embeddings
        # For now, fall back to default routing
        return await self.route(message, context)

