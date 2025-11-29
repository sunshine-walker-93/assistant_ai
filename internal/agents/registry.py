"""Agent registry for managing and routing to agents."""

from typing import Dict, Optional, List
import logging
from .base import BaseAgent, AgentMetadata

logger = logging.getLogger(__name__)


class AgentRegistry:
    """Registry for managing AI agents."""
    
    def __init__(self):
        self._agents: Dict[str, BaseAgent] = {}
    
    def register(self, agent: BaseAgent) -> None:
        """
        Register an agent.
        
        Args:
            agent: Agent instance to register
        """
        name = agent.metadata.name
        if name in self._agents:
            logger.warning(f"Agent '{name}' already registered, overwriting")
        
        self._agents[name] = agent
        logger.info(f"Registered agent: {name} - {agent.metadata.description}")
    
    def unregister(self, name: str) -> bool:
        """
        Unregister an agent.
        
        Args:
            name: Agent name
            
        Returns:
            True if agent was found and removed, False otherwise
        """
        if name in self._agents:
            del self._agents[name]
            logger.info(f"Unregistered agent: {name}")
            return True
        return False
    
    def get(self, name: str) -> Optional[BaseAgent]:
        """
        Get an agent by name.
        
        Args:
            name: Agent name
            
        Returns:
            Agent instance or None if not found
        """
        return self._agents.get(name)
    
    def list_agents(self) -> List[AgentMetadata]:
        """
        List all registered agents.
        
        Returns:
            List of agent metadata
        """
        return [agent.get_metadata() for agent in self._agents.values()]
    
    def list_active_agents(self) -> List[AgentMetadata]:
        """
        List all active agents.
        
        Returns:
            List of active agent metadata
        """
        return [
            agent.get_metadata() 
            for agent in self._agents.values() 
            if agent.is_available()
        ]
    
    def get_default_agent(self) -> Optional[BaseAgent]:
        """
        Get the default agent (first active agent).
        
        Returns:
            Default agent or None if no agents available
        """
        for agent in self._agents.values():
            if agent.is_available():
                return agent
        return None

