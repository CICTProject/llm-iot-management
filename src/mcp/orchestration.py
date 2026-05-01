"""
Orchestration: Creates detailed execution plans for IoT sensor network operations based on medical staff intent and system constraints.

Key functionalities:
- Create orchestration plans based on medical staff intent and system constraints
- Generate detailed execution plans with device assignments, activation sequence, and resource allocation
"""

import logging
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from . import mcp_server
from src.db.database import get_db_client

from src.utils.system import (
    list_all_devices_from_registry,
    query_deployment_status,
    save_orchestration_plan,
)

logger = logging.getLogger(__name__)


# Device orchestration: detailed execution plan 
@mcp_server.tool(name="create_orchestration_plan")
async def create_orchestration_plan(
    intent: str,
    target_zone: str,
    required_services: List[str],
    priority: str = "normal",
    duration_minutes: int = 60,
    algorithm: str = "naive",
) -> Dict[str, Any]:
    """
    Create an orchestration plan based on medical staff intent and system constraints.
    
    Args:
        plan_id: Unique identifier for the orchestration plan (generated if not provided).
        name: Descriptive name for the orchestration plan.
        description: Detailed description of the orchestration plan and its objectives from user intent.
        status: Current status of the orchestration plan (pending, active, completed, failed).
        created_at: Timestamp when the orchestration plan was created.
        devices: List of devices assigned to the orchestration plan with their details (device_id, type, services, location, battery).
        activation_algorithm: The algorithm used for device activation (e.g., naive, cellulaire, probabilistic).
    
    Returns:
        Orchestration plan with device assignments, activation sequence, timeline, resource allocation, and validation status.
    """
    try:
        if not algorithm:
            algorithm = "naive"

        # Get deployment status from database
        deployment_status = query_deployment_status()
        
        if not deployment_status or not deployment_status.get("devices"):
            # Fallback to device registry if InfluxDB is empty
            devices = list_all_devices_from_registry()
        else:
            devices = deployment_status.get("devices", [])
        
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
        

        # Generate plan_id from timestamp (unique per minute+second)
        plan_id = f"orch_plan_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        plan = {
            "plan_id": plan_id,
            "name": f"Orchestration Plan for {intent}",
            "description": f"Plan to {intent} in zone {target_zone} with services {', '.join(required_services)} and priority {priority}",
            "created_at": datetime.now().isoformat(),
            "status": "pending",
            "duration_minutes": duration_minutes,
            "devices": [
                {
                    "device_id": d.get("device_id"),
                    "device_type": d.get("device_type"),
                    "services": d.get("services", []),
                    "location": (d.get("x"), d.get("y"), d.get("z")),
                    "battery_level": d.get("battery_level"),
                }
                for d in assigned_devices
            ],
            "activation_algorithm": algorithm,
        }
        
        logger.info(f"Created orchestration plan {plan_id} in database")
        save_orchestration_plan(plan)
        return plan
    
    except Exception as e:
        logger.error(f"Failed to create orchestration plan: {e}", exc_info=True)
        raise


