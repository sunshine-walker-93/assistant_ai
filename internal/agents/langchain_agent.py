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
        # Normalize inputs: treat empty strings as None
        api_key_original = api_key
        base_url_original = base_url
        api_key = api_key.strip() if api_key else None
        base_url = base_url.strip() if base_url else None
        
        # Log normalized values for debugging
        logger.debug(f"LangChainAgent init - api_key: {'set' if api_key else 'None'}, base_url: {base_url if base_url else 'None'}")
        
        # Determine if using local model or OpenAI API
        has_base_url = base_url is not None and base_url != ""
        has_valid_api_key = api_key is not None and api_key != "" and api_key != "not-needed"
        
        logger.debug(f"LangChainAgent validation - has_base_url: {has_base_url}, has_valid_api_key: {has_valid_api_key}")
        
        # Check if agent should be active
        # For local model: base_url must be provided
        # For OpenAI API: valid api_key must be provided (not empty, not "not-needed")
        is_local_model = has_base_url
        is_openai_api = not has_base_url and has_valid_api_key
        is_active = is_local_model or is_openai_api
        
        logger.debug(f"LangChainAgent status - is_local_model: {is_local_model}, is_openai_api: {is_openai_api}, is_active: {is_active}")
        
        # Validate configuration
        if not is_active:
            if base_url is None and (api_key is None or api_key == ""):
                logger.warning("LangChainAgent initialized without API key or base_url, agent is inactive")
                logger.warning(f"  To activate: Set OPENAI_API_KEY (for OpenAI API) or OPENAI_BASE_URL (for local models)")
            elif base_url is None and api_key == "not-needed":
                logger.error("Invalid configuration: Cannot use 'not-needed' as API key for OpenAI API. "
                           "Please set OPENAI_API_KEY to a valid key or set OPENAI_BASE_URL for local models.")
            else:
                logger.warning("LangChainAgent configuration invalid, agent is inactive")
                logger.warning(f"  api_key: {'set' if api_key else 'None'}, base_url: {base_url if base_url else 'None'}")
        
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
                
                # Set API key based on configuration type
                if is_local_model:
                    # For local models: use provided api_key or "not-needed" placeholder
                    if api_key and api_key != "not-needed":
                        llm_params["openai_api_key"] = api_key
                    else:
                        # For local models without auth, use a placeholder
                        llm_params["openai_api_key"] = "not-needed"
                    llm_params["base_url"] = base_url
                    logger.info(f"LangChainAgent initialized with local model: {model_name} at {base_url}")
                elif is_openai_api:
                    # For OpenAI API: must have valid API key
                    # Double-check that we have a valid API key before creating LLM
                    if not api_key or api_key == "" or api_key == "not-needed":
                        raise ValueError("Invalid API key for OpenAI API. Cannot use 'not-needed' without base_url.")
                    llm_params["openai_api_key"] = api_key
                    logger.info(f"LangChainAgent initialized with OpenAI model: {model_name}")
                
                self.llm = ChatOpenAI(**llm_params)
            except Exception as e:
                logger.error(f"Failed to initialize LangChainAgent: {e}", exc_info=True)
                # Disable agent if initialization fails
                self.metadata.is_active = False
                self.llm = None
        else:
            self.llm = None
            # Store configuration info for error messages
            self._config_info = {
                "api_key_set": api_key is not None,
                "api_key_value": "not-needed" if api_key == "not-needed" else ("set" if api_key else "None"),
                "base_url_set": base_url is not None,
                "base_url_value": base_url if base_url else "None"
            }
    
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
            config_info = getattr(self, '_config_info', {})
            api_key_status = config_info.get('api_key_value', 'unknown')
            base_url_status = config_info.get('base_url_value', 'unknown')
            
            if api_key_status == "not-needed" and base_url_status == "None":
                return "Error: LangChain agent is not active. Invalid configuration: OPENAI_API_KEY='not-needed' but OPENAI_BASE_URL is not set. " \
                       "Please set OPENAI_BASE_URL (for local models) or set OPENAI_API_KEY to a valid key (for OpenAI API)."
            else:
                return "Error: LangChain agent is not active. Please configure OPENAI_API_KEY (for OpenAI API) or OPENAI_BASE_URL (for local models)."
        
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
            error_msg = str(e)
            error_type = type(e).__name__
            logger.error(f"Error in LangChainAgent.process: {error_type}: {error_msg}", exc_info=True)
            
            # Provide more helpful error messages for common issues
            if "connection" in error_msg.lower() or "connect" in error_msg.lower() or "APIConnectionError" in error_type:
                # Connection error - check configuration
                if hasattr(self, 'llm') and self.llm:
                    base_url = getattr(self.llm, 'openai_api_base', None) or "OpenAI API"
                    return f"Error: Connection failed to {base_url}. " \
                           f"Please check: 1) If using local model, ensure the service is running and OPENAI_BASE_URL is correct. " \
                           f"2) If using OpenAI API, check your network connection and OPENAI_API_KEY."
                else:
                    return f"Error: Connection error. {error_msg}"
            elif "invalid_api_key" in error_msg.lower() or "incorrect api key" in error_msg.lower():
                return f"Error: Invalid API key. Please check your OPENAI_API_KEY environment variable. " \
                       f"If using a local model, ensure OPENAI_BASE_URL is set correctly."
            elif "api key" in error_msg.lower():
                return f"Error: API key issue. {error_msg}"
            else:
                return f"Error: Failed to process message. {error_type}: {error_msg}"
    
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
            config_info = getattr(self, '_config_info', {})
            api_key_status = config_info.get('api_key_value', 'unknown')
            base_url_status = config_info.get('base_url_value', 'unknown')
            
            if api_key_status == "not-needed" and base_url_status == "None":
                yield "Error: LangChain agent is not active. Invalid configuration: OPENAI_API_KEY='not-needed' but OPENAI_BASE_URL is not set. " \
                      "Please set OPENAI_BASE_URL (for local models) or set OPENAI_API_KEY to a valid key (for OpenAI API)."
            else:
                yield "Error: LangChain agent is not active. Please configure OPENAI_API_KEY (for OpenAI API) or OPENAI_BASE_URL (for local models)."
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
            error_msg = str(e)
            error_type = type(e).__name__
            logger.error(f"Error in LangChainAgent.process_stream: {error_type}: {error_msg}", exc_info=True)
            
            # Provide more helpful error messages for common issues
            if "connection" in error_msg.lower() or "connect" in error_msg.lower() or "APIConnectionError" in error_type:
                # Connection error - check configuration
                if hasattr(self, 'llm') and self.llm:
                    # Try to get base_url from llm if available
                    base_url = getattr(self.llm, 'openai_api_base', None) or "OpenAI API"
                    yield f"Error: Connection failed to {base_url}. " \
                          f"Please check: 1) If using local model, ensure the service is running and OPENAI_BASE_URL is correct. " \
                          f"2) If using OpenAI API, check your network connection and OPENAI_API_KEY."
                else:
                    yield f"Error: Connection error. {error_msg}"
            elif "invalid_api_key" in error_msg.lower() or "incorrect api key" in error_msg.lower():
                yield f"Error: Invalid API key. Please check your OPENAI_API_KEY environment variable. " \
                      f"If using a local model, ensure OPENAI_BASE_URL is set correctly."
            elif "api key" in error_msg.lower():
                yield f"Error: API key issue. {error_msg}"
            else:
                yield f"Error: Failed to process message. {error_type}: {error_msg}"

