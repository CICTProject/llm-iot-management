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
    get_deployment_status,
    get_network_topology,
    list_medical_devices,
    find_available_devices,
    get_device_details,
    query_devices_by_capability,
    read_medical_metric,
    read_multiple_medical_metrics,
    get_metric_history,
    get_active_deployment_alarms,
    execute_device_command,
)

from .orchestration import (
    create_orchestration_plan,
    get_orchestration_plan,
    list_orchestration_plans,
    cancel_orchestration_plan,
    activate_devices,
    deactivate_devices,
    get_orchestration_status,
    get_device_orchestration_status,
    select_activation_strategy,
    apply_activation_algorithm,
)

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
        "topology": (get_network_topology, []),
        "alarms": (get_active_deployment_alarms, ["priority"]),
        "list": (list_medical_devices, ["zone", "device_type", "required_service", "status"]),
        "find": (find_available_devices, ["zone", "required_service"]),
        "details": (get_device_details, ["device_id"]),
        "query": (query_devices_by_capability, ["service_name"]),
        "read": (read_medical_metric, ["device_id", "metric"]),
        "read_multi": (read_multiple_medical_metrics, ["requests"]),
        "history": (get_metric_history, ["device_id", "hours", "metric", "aggregation"]),
        "execute": (execute_device_command, ["device_id", "command", "parameters"]),
    }


# Device Orchestration Task Tool
class DeviceOrchestrationTool(BaseMCPTool):
    """Unified tool for device orchestration agent.
    
    Sub-tasks for IoT device deployment orchestration, activation planning,
    and resource management.
    
    Sub-tasks:
        Plans: create, get, list, cancel, validate
        Devices: activate, deactivate, status
        Strategy: select, apply
        Resources: allocation, status
    """
    
    name: str = "orchestration"
    description: str = "Orchestrate IoT device deployment, activation, and resource management"
    
    operations: Dict[str, Tuple[Any, Optional[List[str]]]] = {
        # Plan management
        "create_plan": (create_orchestration_plan, ["intent", "target_zone", "required_services", "priority", "duration_minutes"]),
        "get_plan": (get_orchestration_plan, ["plan_id"]),
        "list_plans": (list_orchestration_plans, ["status", "zone", "priority"]),
        "cancel_plan": (cancel_orchestration_plan, ["plan_id", "reason"]),
        "validate_plan": (validate_orchestration_plan, ["plan_id"]),
        
        # Device activation
        "activate": (activate_devices, ["plan_id", "device_ids", "sequence"]),
        "deactivate": (deactivate_devices, ["plan_id", "device_ids", "reason"]),
        "device_status": (get_device_orchestration_status, ["device_id"]),
        
        # Orchestration monitoring
        "orch_status": (get_orchestration_status, ["plan_id"]),
        "resource_alloc": (get_resource_allocation, ["zone"]),
        
        # Strategy and algorithms
        "select_strategy": (select_activation_strategy, ["target_zone", "required_services", "optimization_goal"]),
        "apply_algorithm": (apply_activation_algorithm, ["plan_id", "algorithm", "zone", "parameters"]),
        
        # Fallback to deployment tools
        "list": (list_medical_devices, ["zone", "device_type", "status"]),
        "details": (get_device_details, ["device_id"]),
        "execute": (execute_device_command, ["device_id", "command", "parameters"]),
    }

# Plan Validation Task Tool
class PlanValidationTool(BaseMCPTool):
    """Unified tool for plan validation agent.
    
    Sub-tasks for validating deployment plans and device configurations.
    """
    
    name: str = "plan_validator"
    description: str = "Validate deployment plans and configurations"
    
    operations: Dict[str, Tuple[Any, Optional[List[str]]]] = {
        "status": (get_deployment_status, []),
        "topology": (get_network_topology, []),
        "list": (list_medical_devices, ["zone", "device_type", "status"]),
        "details": (get_device_details, ["device_id"]),
        "query": (query_devices_by_capability, ["service_name"]),
    }

# Edge Anomaly Detection Task Tool
class EdgeAnomalyDetectionTool(BaseMCPTool):
    """Unified tool for edge anomaly detection agent.
    
    Sub-tasks for detecting sensor anomalies and device malfunctions.
    """
    
    name: str = "edge_anomaly"
    description: str = "Detect anomalies in sensor data and device health"
    
    operations: Dict[str, Tuple[Any, Optional[List[str]]]] = {
        "read": (read_medical_metric, ["device_id", "metric"]),
        "read_multi": (read_multiple_medical_metrics, ["requests"]),
        "history": (get_metric_history, ["device_id", "hours", "metric", "aggregation"]),
        "alarms": (get_active_deployment_alarms, ["priority"]),
        "list": (list_medical_devices, ["zone", "status"]),
    }


# Factory function to get MCP tool by task type
def get_mcp_tool(tool_type: str = "deployment") -> BaseMCPTool:
    """Factory function to get MCP tool by task type."""
    tools = {
        "deployment": DeploymentMonitoringTool(),
        "orchestration": DeviceOrchestrationTool(),
        "validation": PlanValidationTool(),
        "edge": EdgeAnomalyDetectionTool(),
    }
    return tools.get(tool_type, DeploymentMonitoringTool())
    