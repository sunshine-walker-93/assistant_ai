"""LangChain-based AI agent implementation using OpenAI."""

import logging
from typing import Dict, Any, Optional, AsyncIterator
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from .base import BaseAgent, AgentMetadata

logger = logging.getLogger(__name__)


class LangChainAgent(BaseAgent):
    """LangChain-based AI agent using OpenAI's ChatOpenAI (supports local models)."""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, 
                 model_name: str = "gpt-3.5-turbo", temperature: float = 0.7):
        """
        Initialize LangChain agent.
        
        Args:
            api_key: OpenAI API key. For local models, can be any string or "not-needed".
                    If None and base_url is also None, agent will be inactive.
            base_url: Custom base URL for local models (e.g., "http://localhost:11434/v1" for Ollama,
                     "http://localhost:8080/v1" for LocalAI). If None, uses OpenAI's default.
            model_name: Model name (default: gpt-3.5-turbo)
                       For Ollama: e.g., "llama2", "mistral", "qwen"
                       For LocalAI: depends on configured models
            temperature: Model temperature (default: 0.7)
        """
        # Check if agent should be active
        # Active if base_url is provided (local model) OR api_key is provided (OpenAI)
        is_active = (base_url is not None and base_url.strip() != "") or \
                   (api_key is not None and api_key.strip() != "")
        
        metadata = AgentMetadata(
            name="langchain",
            description="AI agent powered by LangChain and OpenAI (supports local models)",
            capabilities=["chat", "ai", "openai", "langchain"],
            is_active=is_active
        )
        super().__init__(metadata)
        
        if is_active:
            try:
                # Build ChatOpenAI parameters
                llm_params = {
                    "model": model_name,
                    "temperature": temperature,
                    "streaming": True  # Enable streaming for process_stream
                }
                
                # Set API key (for local models, can be a placeholder)
                if api_key:
                    llm_params["openai_api_key"] = api_key
                elif base_url:
                    # For local models without auth, use a placeholder
                    llm_params["openai_api_key"] = "not-needed"
                
                # Set base URL for local models
                if base_url:
                    llm_params["base_url"] = base_url
                    logger.info(f"LangChainAgent initialized with local model at {base_url}")
                
                self.llm = ChatOpenAI(**llm_params)
                
                if base_url:
                    logger.info(f"LangChainAgent initialized with local model: {model_name} at {base_url}")
                else:
                    logger.info(f"LangChainAgent initialized with OpenAI model: {model_name}")
            except Exception as e:
                logger.error(f"Failed to initialize LangChainAgent: {e}", exc_info=True)
                # Disable agent if initialization fails
                self.metadata.is_active = False
                self.llm = None
        else:
            logger.warning("LangChainAgent initialized without API key or base_url, agent is inactive")
            self.llm = None
    
    async def process(self, message: str, context: Dict[str, Any] = None) -> str:
        """
        Process a user message and return AI response.
        
        Args:
            message: User message/query
            context: Additional context information (may contain conversation history)
            
        Returns:
            AI response text
        """
        if not self.metadata.is_active or self.llm is None:
            return "Error: LangChain agent is not active. Please configure OPENAI_API_KEY or OPENAI_BASE_URL."
        
        try:
            logger.info(f"LangChainAgent processing: {message[:100]}...")
            
            # Build messages from context if available
            messages = []
            
            # Add conversation history from context if present
            if context and "messages" in context:
                history = context.get("messages", [])
                for msg in history:
                    if isinstance(msg, dict):
                        role = msg.get("role", "")
                        content = msg.get("content", "")
                        if role == "user":
                            messages.append(HumanMessage(content=content))
                        elif role == "assistant":
                            messages.append(AIMessage(content=content))
            
            # Add current user message
            messages.append(HumanMessage(content=message))
            
            # Get response from LLM
            response = await self.llm.ainvoke(messages)
            
            # Extract content from response
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            logger.info(f"LangChainAgent response generated: {len(response_text)} characters")
            return response_text
            
        except Exception as e:
            logger.error(f"Error in LangChainAgent.process: {e}", exc_info=True)
            return f"Error: Failed to process message. {str(e)}"
    
    async def process_stream(self, message: str, context: Dict[str, Any] = None) -> AsyncIterator[str]:
        """
        Process a user message and yield streaming responses.
        
        Args:
            message: User message/query
            context: Additional context information (may contain conversation history)
            
        Yields:
            Response chunks
        """
        if not self.metadata.is_active or self.llm is None:
            yield "Error: LangChain agent is not active. Please configure OPENAI_API_KEY or OPENAI_BASE_URL."
            return
        
        try:
            logger.info(f"LangChainAgent processing stream: {message[:100]}...")
            
            # Build messages from context if available
            messages = []
            
            # Add conversation history from context if present
            if context and "messages" in context:
                history = context.get("messages", [])
                for msg in history:
                    if isinstance(msg, dict):
                        role = msg.get("role", "")
                        content = msg.get("content", "")
                        if role == "user":
                            messages.append(HumanMessage(content=content))
                        elif role == "assistant":
                            messages.append(AIMessage(content=content))
            
            # Add current user message
            messages.append(HumanMessage(content=message))
            
            # Stream responses from LLM
            async for chunk in self.llm.astream(messages):
                # Extract content from chunk
                chunk_text = chunk.content if hasattr(chunk, 'content') else str(chunk)
                if chunk_text:
                    yield chunk_text
                    
        except Exception as e:
            logger.error(f"Error in LangChainAgent.process_stream: {e}", exc_info=True)
            yield f"Error: Failed to process message. {str(e)}"

