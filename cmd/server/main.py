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

