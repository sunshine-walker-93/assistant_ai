"""gRPC server entry point."""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import grpc
from concurrent import futures

# Import generated protobuf code
api_path = project_root.parent / "assistant_ai_api" / "python"
if api_path.exists():
    sys.path.insert(0, str(api_path))

try:
    from pb.ai.v1 import ai_pb2_grpc
except ImportError as e:
    print(f"Error: Could not import generated protobuf code: {e}")
    print(f"Please run 'make gen-proto' in assistant_ai_api directory")
    sys.exit(1)

from internal.config.config import load_config
from internal.agents.registry import AgentRegistry
from internal.agents.router import AgentRouter
from internal.agents.simple_agent import SimpleAgent
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
    
    # Register default agent
    simple_agent = SimpleAgent()
    registry.register(simple_agent)
    
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

