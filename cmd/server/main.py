"""gRPC server entry point."""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add project root to path
# Handle both direct execution and module execution
if __file__:
    project_root = Path(__file__).parent.parent.parent
else:
    # Fallback: use current working directory
    project_root = Path.cwd()

sys.path.insert(0, str(project_root))

import grpc
from concurrent import futures
from grpc_reflection.v1alpha import reflection

# Import generated protobuf code from installed package
# assistant_ai_api is installed via pip from Git repository
try:
    from pb.ai.v1 import ai_pb2_grpc
    from pb.ai.v1 import ai_pb2
except ImportError as e:
    print(f"Error: Could not import generated protobuf code: {e}")
    print("Please ensure assistant_ai_api is installed:")
    print("  pip install git+https://github.com/sunshine-walker-93/assistant_ai_api.git#subdirectory=python")
    import traceback
    traceback.print_exc()
    sys.exit(1)

from internal.config.config import load_config
from internal.agents.registry import AgentRegistry
from internal.agents.router import AgentRouter
from internal.agents.langchain_agent import LangChainAgent
from internal.graph.orchestrator import Orchestrator
from internal.service.ai_service import AIServiceServicer


def setup_logging(log_level: str = "INFO"):
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def create_server(registry: AgentRegistry, router: AgentRouter, orchestrator: Orchestrator):
    """Create and configure gRPC server."""
    from pb.ai.v1 import ai_pb2_grpc
    
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Add servicer
    servicer = AIServiceServicer(registry, router, orchestrator)
    ai_pb2_grpc.add_AIServiceServicer_to_server(servicer, server)
    
    # Enable gRPC reflection for dynamic type discovery
    SERVICE_NAMES = (
        ai_pb2.DESCRIPTOR.services_by_name['AIService'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)
    
    return server


async def serve():
    """Start the gRPC server."""
    config = load_config()
    setup_logging(config.log_level)
    logger = logging.getLogger(__name__)
    
    # Initialize components
    registry = AgentRegistry()
    router = AgentRouter(registry)
    orchestrator = Orchestrator()
    
    # Register agents
    # LangChain agent with OpenAI or local model (if configured)
    # Supports both OpenAI API and local models (Ollama, LocalAI, etc.)
    # Note: We always try to register LangChainAgent, but it will be inactive if not properly configured
    try:
        # Log configuration values (mask API key for security)
        api_key_display = "***" if config.openai_api_key else "None"
        base_url_display = config.openai_base_url if config.openai_base_url else "None"
        logger.info(f"LangChainAgent configuration - OPENAI_API_KEY: {api_key_display}, OPENAI_BASE_URL: {base_url_display}, MODEL: {config.openai_model}")
        
        langchain_agent = LangChainAgent(
            api_key=config.openai_api_key,
            base_url=config.openai_base_url,
            model_name=config.openai_model,
            temperature=config.openai_temperature
        )
        registry.register(langchain_agent)
        
        # Log registration status
        if langchain_agent.metadata.is_active:
            if config.openai_base_url:
                logger.info(f"Registered LangChainAgent (ACTIVE) with local model: {config.openai_model} at {config.openai_base_url}")
            else:
                logger.info(f"Registered LangChainAgent (ACTIVE) with OpenAI model: {config.openai_model}")
        else:
            logger.warning(f"Registered LangChainAgent (INACTIVE) - Please configure OPENAI_API_KEY (for OpenAI API) or OPENAI_BASE_URL (for local models)")
            logger.warning(f"  Current values - OPENAI_API_KEY: {'set' if config.openai_api_key else 'not set'}, OPENAI_BASE_URL: {'set' if config.openai_base_url else 'not set'}")
    except Exception as e:
        logger.error(f"Failed to register LangChainAgent: {e}", exc_info=True)
    
    # Create and start server
    server = create_server(registry, router, orchestrator)
    
    listen_addr = config.grpc_addr
    server.add_insecure_port(listen_addr)
    
    logger.info(f"Starting gRPC server on {listen_addr}")
    await server.start()
    
    try:
        await server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
        await server.stop(grace=5)


if __name__ == "__main__":
    asyncio.run(serve())

