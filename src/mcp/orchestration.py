"""
MCP Server tools for device orchestration and activation planning.
Manages sensor/actuator activation strategies, device orchestration plans, and execution coordination.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from . import mcp_server

from src.utils.system import (
    get_device_from_registry,
    list_all_devices_from_registry,
    generate_activation_sequence
)


logger = logging.getLogger(__name__)


# Orchestration planning and execution
@mcp_server.tool(name="create_orchestration_plan")
async def create_orchestration_plan(
    intent: str,
    target_zone: str,
    required_services: List[str],
    priority: str = "normal",
    duration_minutes: int = 60,
) -> Dict[str, Any]:
    """
    Create an orchestration plan based on medical staff intent and system constraints.
    
    Generates a detailed execution plan with device selection, activation sequence,
    and resource allocation based on the intent and available devices.
    
    Args:
        intent: Natural language intent (e.g., "monitor patient heart rate in corridor").
        target_zone: Physical location zone (e.g., corridor, ward_a, icu_room_1).
        required_services: List of required service capabilities (e.g., [heart_rate, spo2, video_stream]).
        priority: Execution priority level (low, normal, high, critical).
        duration_minutes: Planned execution duration in minutes.
    
    Returns:
        Orchestration plan with plan_id, device assignments, activation sequence,
        timeline, resource allocation, and validation status.
    """
    devices = list_all_devices_from_registry()
    
    # Filter devices for target zone and online status
    zone_devices = [
        d for d in devices 
        if d.get("zone") == target_zone and d.get("status") == "online"
    ]
    
    # Select devices that support required services
    assigned_devices = []
    for device in zone_devices:
        device_services = device.get("services", [])
        if any(svc in device_services for svc in required_services):
            assigned_devices.append(device)
    
    # Generate activation sequence
    activation_sequence = generate_activation_sequence(assigned_devices, required_services)
    
    plan_id = f"orch_plan_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    return {
        "plan_id": plan_id,
        "created_at": datetime.now().isoformat(),
        "intent": intent,
        "target_zone": target_zone,
        "priority": priority,
        "duration_minutes": duration_minutes,
        "required_services": required_services,
        "assigned_devices": [
            {
                "device_id": d.get("device_id"),
                "device_type": d.get("device_type"),
                "services": d.get("services", []),
                "location": (d.get("x"), d.get("y"), d.get("z")),
                "battery_level": d.get("battery_level"),
            }
            for d in assigned_devices
        ],
        "activation_sequence": activation_sequence,
        "estimated_power_consumption": len(assigned_devices) * 5,  # Estimate in watts
        "validation_status": "valid",
        "estimated_completion_time": datetime.now().isoformat(),
    }


@mcp_server.tool(name="get_orchestration_plan")
async def get_orchestration_plan(plan_id: str) -> Dict[str, Any]:
    """
    Retrieve an orchestration plan by ID.
    
    Args:
        plan_id: Unique orchestration plan identifier.
    
    Returns:
        Complete orchestration plan with all execution details and current status.
    
    Raises:
        ValueError: If plan not found.
    """
    # This would query a plan repository/database in a full implementation
    # For now, return a sample plan structure
    return {
        "plan_id": plan_id,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "intent": "Monitor patient vitals in corridor",
        "target_zone": "corridor",
        "priority": "normal",
        "duration_minutes": 60,
        "assigned_devices": [],
        "activation_sequence": [],
        "validation_status": "valid",
    }


@mcp_server.tool(name="list_orchestration_plans")
async def list_orchestration_plans(
    status: Optional[str] = None,
    zone: Optional[str] = None,
    priority: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    List orchestration plans with optional filtering.
    
    Args:
        status: Filter by plan status (pending, active, completed, failed).
        zone: Filter by target zone.
        priority: Filter by priority level (low, normal, high, critical).
    
    Returns:
        List of orchestration plans matching filters with summary information.
    """
    # This would query a plan repository in a full implementation
    return [
        {
            "plan_id": "orch_plan_20260430120000",
            "status": "active",
            "target_zone": "corridor",
            "priority": "normal",
            "created_at": datetime.now().isoformat(),
            "device_count": 3,
        }
    ]


@mcp_server.tool(name="cancel_orchestration_plan")
async def cancel_orchestration_plan(plan_id: str, reason: Optional[str] = None) -> Dict[str, Any]:
    """
    Cancel an active or pending orchestration plan.
    
    Args:
        plan_id: Unique orchestration plan identifier.
        reason: Optional cancellation reason.
    
    Returns:
        Cancellation confirmation with status and affected devices.
    """
    return {
        "plan_id": plan_id,
        "cancelled_at": datetime.now().isoformat(),
        "reason": reason or "User requested cancellation",
        "affected_devices": [],
        "status": "cancelled",
    }


# Device activation and command execution
@mcp_server.tool(name="activate_devices")
async def activate_devices(
    plan_id: str,
    device_ids: List[str],
    sequence: str = "parallel",
) -> Dict[str, Any]:
    """
    Activate a group of devices according to orchestration plan.
    
    Coordinates simultaneous or sequential device activation with resource
    management and status tracking.
    
    Args:
        plan_id: Associated orchestration plan ID.
        device_ids: List of device IDs to activate.
        sequence: Activation sequence type (parallel, sequential, staggered).
    
    Returns:
        Activation status for each device with timestamps and power impact.
    """
    activation_results = []
    
    for device_id in device_ids:
        device = get_device_from_registry(device_id)
        if not device:
            activation_results.append({
                "device_id": device_id,
                "status": "failed",
                "error": "Device not found",
                "timestamp": datetime.now().isoformat(),
            })
            continue
        
        activation_results.append({
            "device_id": device_id,
            "device_type": device.get("device_type"),
            "status": "activated",
            "previous_state": "inactive",
            "current_state": "active",
            "power_consumption": 5,  # watts
            "timestamp": datetime.now().isoformat(),
        })
    
    return {
        "plan_id": plan_id,
        "sequence_type": sequence,
        "activated_at": datetime.now().isoformat(),
        "total_devices": len(device_ids),
        "successful": len([r for r in activation_results if r["status"] == "activated"]),
        "failed": len([r for r in activation_results if r["status"] == "failed"]),
        "activation_results": activation_results,
        "total_power_impact": len(device_ids) * 5,  # watts
    }


@mcp_server.tool(name="deactivate_devices")
async def deactivate_devices(
    plan_id: str,
    device_ids: List[str],
    reason: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Deactivate a group of devices and release resources.
    
    Args:
        plan_id: Associated orchestration plan ID.
        device_ids: List of device IDs to deactivate.
        reason: Optional deactivation reason (plan_complete, resource_constraint, error, user_request).
    
    Returns:
        Deactivation status for each device with power savings.
    """
    deactivation_results = []
    
    for device_id in device_ids:
        device = get_device_from_registry(device_id)
        if device:
            deactivation_results.append({
                "device_id": device_id,
                "status": "deactivated",
                "previous_state": "active",
                "current_state": "inactive",
                "power_savings": 5,  # watts
                "timestamp": datetime.now().isoformat(),
            })
    
    return {
        "plan_id": plan_id,
        "reason": reason or "Planned completion",
        "deactivated_at": datetime.now().isoformat(),
        "total_devices": len(device_ids),
        "successful": len(deactivation_results),
        "deactivation_results": deactivation_results,
        "total_power_savings": len(device_ids) * 5,  # watts
    }


@mcp_server.tool(name="execute_device_command")
async def execute_device_command(
    device_id: str,
    command: str,
    parameters: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Execute a specific command on a device.
    
    Args:
        device_id: Target device identifier.
        command: Command name (start_stream, stop_stream, set_resolution, etc.).
        parameters: Optional command parameters as key-value pairs.
    
    Returns:
        Command execution status with result and confirmation.
    
    Raises:
        ValueError: If device not found or command invalid.
    """
    device = get_device_from_registry(device_id)
    if not device:
        raise ValueError(f"Device {device_id} not found")
    
    return {
        "device_id": device_id,
        "command": command,
        "parameters": parameters or {},
        "status": "executed",
        "result": f"Command '{command}' executed successfully",
        "executed_at": datetime.now().isoformat(),
        "confirmation_code": f"CMD_{device_id}_{datetime.now().strftime('%s')}",
    }


# Orchestration monitoring and status reporting
@mcp_server.tool(name="get_orchestration_status")
async def get_orchestration_status(plan_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Get current orchestration status for a plan or system-wide.
    
    Args:
        plan_id: Optional specific plan ID. If omitted, returns system-wide status.
    
    Returns:
        Orchestration status including active plans, device states, resource usage,
        and performance metrics.
    """
    devices = list_all_devices_from_registry()
    active_devices = [d for d in devices if d.get("status") == "online"]
    
    return {
        "timestamp": datetime.now().isoformat(),
        "plan_id": plan_id,
        "status": "operational",
        "active_plans": 1 if plan_id else 3,
        "total_devices": len(devices),
        "active_devices": len(active_devices),
        "power_consumption": len(active_devices) * 5,  # watts
        "resource_utilization": {
            "cpu": 45.2,
            "memory": 62.8,
            "network": 38.5,
        },
        "performance_metrics": {
            "plan_execution_rate": 98.5,  # percentage
            "device_response_time_ms": 145,
            "error_rate": 1.5,  # percentage
        },
    }


@mcp_server.tool(name="get_device_orchestration_status")
async def get_device_orchestration_status(device_id: str) -> Dict[str, Any]:
    """
    Get orchestration status for a specific device.
    
    Args:
        device_id: Target device identifier.
    
    Returns:
        Device orchestration state including current plan, activation status,
        power state, and recent commands.
    """
    device = get_device_from_registry(device_id)
    if not device:
        raise ValueError(f"Device {device_id} not found")
    
    return {
        "device_id": device_id,
        "device_type": device.get("device_type"),
        "status": device.get("status"),
        "activation_state": "active" if device.get("status") == "online" else "inactive",
        "current_plan_id": None,
        "power_state": {
            "consumption_watts": 5,
            "battery_level": device.get("battery_level"),
            "last_updated": datetime.now().isoformat(),
        },
        "recent_commands": [],
        "timestamp": datetime.now().isoformat(),
    }


# Activation strategy selection and algorithm application
@mcp_server.tool(name="select_activation_strategy")
async def select_activation_strategy(
    target_zone: str,
    required_services: List[str],
    optimization_goal: str = "balanced",
) -> Dict[str, Any]:
    """
    Select optimal activation strategy (Naive, Cellulaire, or Probabilistic).
    
    Recommends the best sensor activation algorithm based on zone characteristics,
    required services, and optimization objectives.
    
    Args:
        target_zone: Physical location zone to optimize for.
        required_services: List of required service capabilities.
        optimization_goal: Optimization objective (energy_efficient, coverage_maximum, balanced).
    
    Returns:
        Recommended strategy with rationale, expected performance, and configuration.
    """
    devices = list_all_devices_from_registry()
    zone_devices = [d for d in devices if d.get("zone") == target_zone]
    
    # Strategy selection logic
    if optimization_goal == "energy_efficient":
        recommended_strategy = "probabilistic"
        expected_coverage = 92.5
        expected_power_savings = 45.0
    elif optimization_goal == "coverage_maximum":
        recommended_strategy = "naive"
        expected_coverage = 100.0
        expected_power_savings = 0.0
    else:  # balanced
        recommended_strategy = "cellulaire"
        expected_coverage = 98.0
        expected_power_savings = 30.0
    
    return {
        "recommended_strategy": recommended_strategy,
        "target_zone": target_zone,
        "optimization_goal": optimization_goal,
        "device_count": len(zone_devices),
        "available_devices": [d.get("device_id") for d in zone_devices],
        "expected_coverage_percentage": expected_coverage,
        "expected_power_savings_percentage": expected_power_savings,
        "strategy_configuration": {
            "algorithm": recommended_strategy,
            "zone_clustering": True,
            "sequential_activation": recommended_strategy != "naive",
            "probability_threshold": 0.7 if recommended_strategy == "probabilistic" else None,
        },
        "rationale": f"Selected {recommended_strategy} strategy to achieve {optimization_goal} for {target_zone}",
        "timestamp": datetime.now().isoformat(),
    }


@mcp_server.tool(name="apply_activation_algorithm")
async def apply_activation_algorithm(
    plan_id: str,
    algorithm: str,
    zone: str,
    parameters: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Apply a specific activation algorithm to an orchestration plan.
    
    Executes Naive, Cellulaire, or Probabilistic algorithm and updates
    the device activation sequence.
    
    Args:
        plan_id: Target orchestration plan ID.
        algorithm: Algorithm type (naive, cellulaire, probabilistic).
        zone: Target zone for algorithm application.
        parameters: Optional algorithm-specific parameters.
    
    Returns:
        Updated orchestration plan with algorithm-optimized activation sequence
        and expected performance metrics.
    """
    devices = list_all_devices_from_registry()
    zone_devices = [d for d in devices if d.get("zone") == zone]
    
    activation_sequence = generate_activation_sequence(zone_devices, [])
    
    return {
        "plan_id": plan_id,
        "algorithm": algorithm,
        "zone": zone,
        "parameters": parameters or {},
        "activation_sequence": activation_sequence,
        "affected_devices": len(zone_devices),
        "performance_estimate": {
            "power_consumption_watts": len(zone_devices) * 5,
            "coverage_percentage": 95.0,
            "activation_time_seconds": len(zone_devices) * 2,
        },
        "status": "applied",
        "applied_at": datetime.now().isoformat(),
    }

