"""
MCP Tools for CrewAI - Task-specific unified wrappers.
Each tool wraps async MCP functions as sub-tasks for specific agent roles.
"""
import json
import asyncio
import logging
from typing import Any, Dict, Tuple, List, Optional

from pydantic import ConfigDict
from crewai.tools import BaseTool

from .deployment import (
    get_device_details,
    read_medical_metric,
    read_multiple_medical_metrics,
)

from .orchestration import (
    create_orchestration_plan,
)

from .plan_validation import (
    get_deployment_status,
    recommend_activation_algorithm,
)

from .plan_execution import execute_plan

logger = logging.getLogger(__name__)


def _async(coro):
    """Run async function in sync context."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


# Base class for MCP tools with unified async execution and error handling.
class BaseMCPTool(BaseTool):
    """Base class for MCP tools."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    # Declare operations as a dict of task name to (function, expected_args)
    operations: Dict[str, Tuple[Any, Optional[List[str]]]] = {}
    
    def _run(self, query: str) -> str:
        try:
            # Parse JSON query or default to empty task
            params = json.loads(query) if query.startswith("{") else {"task": "default"}
            task = params.get("task", "default")
            args = params.get("args", {})
            
            # Ensure args is a dictionary
            if isinstance(args, str):
                args = json.loads(args) if args.startswith("{") else {}
            elif not isinstance(args, dict):
                args = {}
            
            if task not in self.operations:
                return json.dumps({
                    "error": f"Unknown task: {task}",
                    "available_tasks": list(self.operations.keys())
                })
            
            func, expected_args = self.operations[task]
            filtered_args = {k: v for k, v in args.items() if k in (expected_args or [])}
            
            result = _async(func(**filtered_args))
            return json.dumps({"success": True, "data": result})
        except Exception as e:
            logger.error(f"MCP error: {e}", exc_info=True)
            return json.dumps({"error": str(e)})


# Deployment Monitoring Task Tool
class DeploymentMonitoringTool(BaseMCPTool):
    """Unified tool for deployment monitoring agent.
    
    Sub-tasks:
        Monitoring: status, topology, alarms
        Devices: list, find, details, query
        Metrics: read, read_multi, history
        Commands: execute
    """
    
    name: str = "deployment_monitor"
    description: str = "Monitor deployment, devices, metrics, alarms and execute commands"
    
    operations: Dict[str, Tuple[Any, Optional[List[str]]]] = {
        "status": (get_deployment_status, []),
        "details": (get_device_details, ["device_id"]),
        "read": (read_medical_metric, ["device_id", "metric"]),
        "read_multi": (read_multiple_medical_metrics, ["requests"]),
    }


# Device Orchestration Task Tool
class DeviceOrchestrationTool(BaseMCPTool):
    """Unified tool for device orchestration agent.
    
    Sub-tasks for IoT device deployment orchestration, activation planning,
    and resource management.
    
    Sub-tasks:
        create_plan: Create orchestration plan
    """
    
    name: str = "orchestration"
    description: str = "Orchestrate IoT device deployment, activation, and resource management"
    
    operations: Dict[str, Tuple[Any, Optional[List[str]]]] = {
        # Plan management
        "create_plan": (create_orchestration_plan, ["intent", "target_zone", "required_services", "priority", "duration_minutes"]),
        
        # Deployment status for orchestration
        "details": (get_device_details, ["device_id"]),
    }

# Plan Validation Task Tool
class PlanValidationTool(BaseMCPTool):
    """Unified tool for plan validation agent.
    
    Sub-tasks for validating deployment plans and device configurations.
    Queries deployment status and executes validation algorithms.
    """
    
    name: str = "plan_validator"
    description: str = "Validate deployment plans and configurations with constraint-based assurance"
    
    operations: Dict[str, Tuple[Any, Optional[List[str]]]] = {
        # Deployment status for validation
        "deployment_status": (get_deployment_status, []),

        # Algorithm recommendation for plan validation
        "recommend_algorithm": (recommend_activation_algorithm, ["devices", "min_accuracy_percent", "max_energy_percent", "activation_duration_seconds"]),
    }

# Plan Execution Task Tool
class PlanExecutionTool(BaseMCPTool):
    """Unified tool for plan execution agent.
    
    Sub-tasks for executing device activation plans and strategies.
    Executes different activation algorithms based on the orchestration plan.
    """
    
    name: str = "plan_execution"
    description: str = "Execute device activation plans with various algorithms and strategies"
    
    operations: Dict[str, Tuple[Any, Optional[List[str]]]] = {
        "execute": (execute_plan, ["plan_id", "target_zone", "required_services"]),
    }

# Edge Anomaly Detection Task Tool (Future work)
class EdgeAnomalyDetectionTool(BaseMCPTool):
    """Unified tool for edge anomaly detection agent.
    
    Sub-tasks for detecting sensor anomalies and device malfunctions.
    """
    
    name: str = "edge_anomaly_detection"
    description: str = "Detect anomalies in sensor data and device health"
    
    operations: Dict[str, Tuple[Any, Optional[List[str]]]] = {
        "read": (read_medical_metric, ["device_id", "metric"]),
        "read_multi": (read_multiple_medical_metrics, ["requests"]),
    }

# Factory function to get MCP tool by task type
def get_mcp_tool(tool_type: str = "deployment") -> BaseMCPTool:
    """Factory function to get MCP tool by task type."""
    tools = {
        "deployment": DeploymentMonitoringTool(),
        "orchestration": DeviceOrchestrationTool(),
        "validation": PlanValidationTool(),
        "execution": PlanExecutionTool(),
        "edge": EdgeAnomalyDetectionTool(),
    }
    return tools.get(tool_type, DeploymentMonitoringTool())
    