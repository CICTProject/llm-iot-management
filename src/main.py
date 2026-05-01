"""FastAPI Server for IoT Orchestration with CrewAI Management."""
import re
import time
import uuid
import logging
import asyncio
from typing import Any, List, Dict, Optional
from enum import Enum
import json

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict
from dotenv import load_dotenv

from src.crew.crew import CustomCrew

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Data models for API requests and responses
class ChatMessage(BaseModel):
    """Chat message model."""
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    """Chat completion request model."""
    model_config = ConfigDict(extra="allow")
    model: str
    messages: List[ChatMessage]
    temperature: Optional[float] = 0
    stream: Optional[bool] = False


class AgentType(str, Enum):
    """Available agent types."""
    ALL = "all"
    EDGE_ANOMALY_DETECTION = "edge_anomaly_detection"
    ORCHESTRATION = "orchestration"
    PLAN_VALIDATION = "plan_validation"
    PLAN_EXECUTION = "plan_execution"
    DEPLOYMENT_MONITORING = "deployment_monitoring"


class CrewExecutionRequest(BaseModel):
    """Crew execution request model."""
    agent_type: AgentType = AgentType.ALL
    context: Optional[Dict[str, Any]] = None


class CrewExecutionResponse(BaseModel):
    """Crew execution response model."""
    execution_id: str
    agent_type: AgentType
    status: str
    result: Optional[Any] = None
    error: Optional[str] = None
    timestamp: float


# Initialize FastAPI app
app = FastAPI(
    title="IoT Deployment Management with CrewAI",
    description="FastAPI server for managing IoT deployment using CrewAI agents",
    version="1.0"
)

# Global application state
CREW: Optional[CustomCrew] = None
CHATGPT_MODEL_ID = "llm-agent-chatgpt"
OLLAMA_MODEL_ID = "llm-agent-ollama"
GEMINI_MODEL_ID = "llm-agent-gemini"

# Execution tracking
execution_history: Dict[str, CrewExecutionResponse] = {}


# App lifecycle events

@app.on_event("startup")
async def startup_event():
    """Initialize crew on startup."""
    global CREW
    try:
        CREW = CustomCrew()
        logger.info("CrewAI initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize CrewAI: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down FastAPI server")


# API endpoints for crew execution

@app.post("/v1/crew/execute", response_model=CrewExecutionResponse)
async def execute_crew(request: CrewExecutionRequest, background_tasks: BackgroundTasks):
    """
    Execute crew agents for IoT orchestration.
    
    Args:

        request: Crew execution request with agent type and context

        background_tasks: FastAPI background tasks
    
    Returns:
        CrewExecutionResponse with execution status and results
    """
    if CREW is None:
        raise HTTPException(status_code=500, detail="Crew not initialized")
    
    execution_id = f"exec-{uuid.uuid4().hex}"
    
    try:
        logger.info(f"Starting crew execution: {execution_id} (Agent: {request.agent_type})")
        
        # Execute appropriate agent based on request
        if request.agent_type == AgentType.ALL:
            result = CREW.run_all()
        elif request.agent_type == AgentType.EDGE_ANOMALY_DETECTION:
            result = CREW.run_edge_anomaly_detection()
        elif request.agent_type == AgentType.ORCHESTRATION:
            result = CREW.run_orchestration()
        elif request.agent_type == AgentType.PLAN_VALIDATION:
            result = CREW.run_plan_validation()
        elif request.agent_type == AgentType.DEPLOYMENT_MONITORING:
            result = CREW.run_deployment_monitoring()
        elif request.agent_type == AgentType.PLAN_EXECUTION:
            result = CREW.run_plan_execution()
        else:
            raise ValueError(f"Unknown agent type: {request.agent_type}")
        
        response = CrewExecutionResponse(
            execution_id=execution_id,
            agent_type=request.agent_type,
            status="success",
            result=result,
            timestamp=time.time()
        )
        
        # Store execution history
        execution_history[execution_id] = response
        logger.info(f"Crew execution completed: {execution_id}")
        
        return response
        
    except Exception as e:
        logger.error(f"Crew execution failed: {e}")
        response = CrewExecutionResponse(
            execution_id=execution_id,
            agent_type=request.agent_type,
            status="error",
            error=str(e),
            timestamp=time.time()
        )
        execution_history[execution_id] = response
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v1/crew/execution/{execution_id}", response_model=CrewExecutionResponse)
async def get_execution_status(execution_id: str):
    """
    Get status and results of a crew execution.
    
    Args:

        execution_id: The execution ID to query
    
    Returns:
        CrewExecutionResponse with execution status
    """
    if execution_id not in execution_history:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    return execution_history[execution_id]


@app.get("/v1/crew/executions")
async def list_executions(limit: int = 10):
    """
    List recent crew executions.
    
    Args:

        limit: Maximum number of executions to return
    
    Returns:
        List of recent executions
    """
    executions = list(execution_history.values())
    executions.sort(key=lambda x: x.timestamp, reverse=True)
    return executions[:limit]


# API endpoints for chat completions

@app.get("/v1/models")
async def list_models():
    """List available models."""
    now = int(time.time())
    return {
        "object": "list",
        "data": [
            {
                "id": CHATGPT_MODEL_ID,
                "object": "model",
                "created": now,
                "owned_by": "local",
            },
            {
                "id": OLLAMA_MODEL_ID,
                "object": "model",
                "created": now,
                "owned_by": "external",
            },
            {
                "id": GEMINI_MODEL_ID,
                "object": "model",
                "created": now,
                "owned_by": "external",
            },
        ],
    }


@app.post("/v1/chat/completions")
async def chat_completions(req: ChatCompletionRequest):
    """
    Process chat completions using crew agents.
    
    Args:

        req: Chat completion request
    
    Returns:
        Chat completion response or streaming response
    """
    if req.model not in [CHATGPT_MODEL_ID, OLLAMA_MODEL_ID, GEMINI_MODEL_ID]:
        raise HTTPException(status_code=400, detail=f"Unknown model: {req.model}")
    
    if CREW is None:
        raise HTTPException(status_code=500, detail="Crew not initialized")
    
    # Extract user message
    user_text = None
    for message in reversed(req.messages):
        if message.role == "user":
            user_text = message.content
            break
    
    if not user_text:
        raise HTTPException(status_code=400, detail="No user message in request")
    
    try:
        # Determine which agent to use based on message content with expanded keywords
        user_lower = user_text.lower()
        
        # Edge Anomaly Detection: sensor data, vital signs, health metrics, anomalies
        edge_keywords = ["anomaly", "detect", "fall", "abnormal", "alert", "heart rate", 
                        "blood pressure", "temperature", "vital", "sensor data", "malfunction",
                        "spo2", "respiration", "glucose", "health metric", "reading"]
        
        # Deployment Monitoring: device status, availability, health, network
        monitoring_keywords = ["status", "deployment", "track", "device", "available", 
                              "online", "offline", "health", "battery", "connection", 
                              "network", "topology", "monitor", "how many", "which devices",
                              "device location", "device list"]
        
        # Orchestration: activate, configure, deploy devices, select devices
        orchestration_keywords = ["orchestrate", "deploy", "configure", "activate", "setup",
                                 "video", "stream", "camera", "sensor", "device select",
                                 "device activation", "plan device", "service"]
        
        # Plan Validation: validate, optimize, verify plan
        validation_keywords = ["validate", "plan", "check", "verify", "optimize", 
                              "algorithm", "energy", "resource", "constraint", "accuracy"]
        
        # Plan Execution: execute, run, start, launch
        execution_keywords = ["execute", "run", "start", "begin", "launch", "activate plan",
                             "execute plan", "http action", "deployment action"]
        
        # Match keywords
        if any(keyword in user_lower for keyword in edge_keywords):
            result = CREW.run_edge_anomaly_detection()
            logger.info(f"Edge Anomaly Detection Agent selected for: {user_text[:50]}...")
        elif any(keyword in user_lower for keyword in orchestration_keywords):
            result = CREW.run_orchestration()
            logger.info(f"Orchestration Agent selected for: {user_text[:50]}...")
        elif any(keyword in user_lower for keyword in validation_keywords):
            result = CREW.run_plan_validation()
            logger.info(f"Plan Validation Agent selected for: {user_text[:50]}...")
        elif any(keyword in user_lower for keyword in execution_keywords):
            result = CREW.run_plan_execution()
            logger.info(f"Plan Execution Agent selected for: {user_text[:50]}...")
        elif any(keyword in user_lower for keyword in monitoring_keywords):
            result = CREW.run_deployment_monitoring()
            logger.info(f"Deployment Monitoring Agent selected for: {user_text[:50]}...")
        else:
            # Default to deployment monitoring for general queries
            logger.warning(f"No specific keyword matched, defaulting to Deployment Monitoring for: {user_text[:50]}...")
            result = CREW.run_deployment_monitoring()

        # Process message and get response with formatting
        if hasattr(result, 'raw'):
            raw_answer = result.raw if isinstance(result.raw, str) else str(result.raw)
        else:
            raw_answer = str(result)
        
        # Parse response to extract clean JSON object
        answer = None
        
        # First try to parse the entire response as JSON
        try:
            answer = json.loads(raw_answer)
        except json.JSONDecodeError:
            pass
        
        # If still no valid JSON, reformat the raw answer into a JSON structure
        if answer is None:
            answer = raw_answer.strip()
            # Extract key-value pairs if possible
            kv_pattern = re.compile(r"(\w+):\s*(.+)")
            kv_matches = kv_pattern.findall(answer)
            if kv_matches:
                answer_dict = {k: v for k, v in kv_matches}
                answer = answer_dict
            # Split all double line breaks into a list if it looks like multiple items
            elif "\n\n" in answer:
                items = [item.strip() for item in answer.split("\n\n") if item.strip()]
                answer = items
        else:
            # If we got a valid JSON, but it's a string, try to parse it again
            if isinstance(answer, str):
                try:
                    answer = json.loads(answer)
                except json.JSONDecodeError:
                    pass
    
    except Exception as e:
        logger.error(f"Chat completion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    completion_id = f"chatcmpl-{uuid.uuid4().hex}"
    now = int(time.time())
    
    # Handle streaming response
    if req.stream:
        async def event_generator():
            chunk = {
                "id": completion_id,
                "object": "chat.completion.chunk",
                "created": now,
                "model": req.model,
                "choices": [{
                    "index": 0,
                    "delta": {"role": "assistant", "content": answer},
                    "finish_reason": None
                }]
            }
            yield f"data: {json.dumps(chunk)}\n\n"
            done = {
                "id": completion_id,
                "object": "chat.completion.chunk",
                "created": now,
                "model": req.model,
                "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}]
            }
            yield f"data: {json.dumps(done)}\n\n"
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(event_generator(), media_type="text/event-stream")
    
    # Return non-streaming response
    return {
        "id": completion_id,
        "object": "chat.completion",
        "created": now,
        "model": req.model,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant", 
                    "content": answer
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
    }


# API endpoints for health and status
@app.get("/v1/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "crew_initialized": CREW is not None,
        "timestamp": time.time()
    }


@app.get("/v1/status")
async def get_status():
    """Get detailed status information."""
    return {
        "status": "running",
        "crew_initialized": CREW is not None,
        "total_executions": len(execution_history),
        "available_agents": [
            AgentType.EDGE_ANOMALY_DETECTION.value,
            AgentType.ORCHESTRATION.value,
            AgentType.PLAN_VALIDATION.value,
            AgentType.DEPLOYMENT_MONITORING.value,
            AgentType.PLAN_EXECUTION.value,
            AgentType.ALL.value,
        ],
        "timestamp": time.time()
    }


# Run the FastAPI app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
