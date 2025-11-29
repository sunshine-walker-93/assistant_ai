"""gRPC service implementation for AI service."""

import logging
from typing import Iterator
import grpc

# Import generated protobuf code
import sys
import os
from pathlib import Path

# Add assistant_ai_api python path
project_root = Path(__file__).parent.parent.parent.parent
api_path = project_root.parent / "assistant_ai_api" / "python"
if api_path.exists():
    sys.path.insert(0, str(api_path))

try:
    from pb.ai.v1 import ai_pb2
    from pb.ai.v1 import ai_pb2_grpc
except ImportError as e:
    logger.error(f"Could not import generated protobuf code: {e}")
    logger.error("Please run 'make gen-proto' in assistant_ai_api directory")
    raise

from ..agents.registry import AgentRegistry
from ..agents.router import AgentRouter
from ..graph.orchestrator import Orchestrator

logger = logging.getLogger(__name__)


class AIServiceServicer(ai_pb2_grpc.AIServiceServicer):
    """gRPC service implementation."""
    
    def __init__(self, registry: AgentRegistry, router: AgentRouter, orchestrator: Orchestrator):
        self.registry = registry
        self.router = router
        self.orchestrator = orchestrator
    
    async def Process(self, request, context):
        """
        Process a user request.
        
        This is the unified entry point that routes to appropriate agent
        or uses LangGraph orchestration for complex workflows.
        """
        try:
            message = request.message
            user_id = request.user_id
            agent_name = request.agent_name if request.agent_name else None
            context_dict = dict(request.context) if request.context else {}
            session_id = request.session_id if request.session_id else None
            
            logger.info(f"Processing request from user {user_id}, message: {message[:100]}...")
            
            # Check if orchestration should be used
            if self.orchestrator.use_orchestration(message, context_dict):
                response_text = await self.orchestrator.orchestrate(message, context_dict)
                selected_agent = "orchestrator"
            else:
                # Route to appropriate agent
                agent = await self.router.route(message, context_dict, agent_name)
                if not agent:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details("No available agent found")
                    return ai_pb2.ProcessResponse(
                        agent_name="",
                        response="No available agent found",
                        metadata={},
                        is_streaming=False,
                        session_id=session_id or ""
                    )
                
                # Process with selected agent
                response_text = await agent.process(message, context_dict)
                selected_agent = agent.metadata.name
            
            # Build response
            return ai_pb2.ProcessResponse(
                agent_name=selected_agent,
                response=response_text,
                metadata={},
                is_streaming=False,
                session_id=session_id or ""
            )
        
        except Exception as e:
            logger.error(f"Error processing request: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return ai_pb2.ProcessResponse(
                agent_name="",
                response=f"Error: {str(e)}",
                metadata={},
                is_streaming=False,
                session_id=""
            )
    
    async def ProcessStream(self, request, context):
        """
        Process a user request with streaming response.
        """
        try:
            message = request.message
            user_id = request.user_id
            agent_name = request.agent_name if request.agent_name else None
            context_dict = dict(request.context) if request.context else {}
            session_id = request.session_id if request.session_id else None
            
            logger.info(f"Processing streaming request from user {user_id}")
            
            # Route to appropriate agent
            agent = await self.router.route(message, context_dict, agent_name)
            if not agent:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("No available agent found")
                return
            
            # Stream responses
            async for chunk in agent.process_stream(message, context_dict):
                yield ai_pb2.ProcessResponse(
                    agent_name=agent.metadata.name,
                    response=chunk,
                    metadata={},
                    is_streaming=True,
                    session_id=session_id or ""
                )
        
        except Exception as e:
            logger.error(f"Error in streaming request: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
    
    async def ListAgents(self, request, context):
        """
        List all available agents.
        """
        try:
            agents = self.registry.list_agents()
            agent_infos = []
            
            for agent_metadata in agents:
                agent_info = ai_pb2.AgentInfo(
                    name=agent_metadata.name,
                    description=agent_metadata.description,
                    capabilities=agent_metadata.capabilities,
                    is_active=agent_metadata.is_active
                )
                agent_infos.append(agent_info)
            
            return ai_pb2.ListAgentsResponse(agents=agent_infos)
        
        except Exception as e:
            logger.error(f"Error listing agents: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return ai_pb2.ListAgentsResponse(agents=[])

