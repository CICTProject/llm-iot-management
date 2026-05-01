"""
Plan Execution: Translates orchestration plans into HTTP-executable instructions for IoT sensor networks.
Implements 3 WSN sensor activation algorithms:
- Algorithm 1.4.1: Naive - All devices activated simultaneously
- Algorithm 1.4.2: Cellulaire - Sequential zone-based activation  
- Algorithm 1.4.3: Probabilistic - Spatial optimization with metaheuristics
"""

import logging
import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from . import mcp_server
from src.utils.system import execute_algorithm, generate_http_actions, query_deployment_status

logger = logging.getLogger(__name__)


# Plan execution: translate orchestration plan into HTTP-executable instructions
@mcp_server.tool(name="execute_plan")
async def execute_plan(
    plan_id: str,
    target_zone: str,
    required_services: List[str],
    algorithm: str = "probabilistic",
) -> Dict[str, Any]:
    """
    Translate orchestration plan into HTTP-executable instructions.
    
    Args:
        plan_id: Orchestration plan identifier
        target_zone: Target deployment zone
        required_services: Required service capabilities
        algorithm: Activation algorithm (naive, sequential, probabilistic)
    
    Returns:
        Execution plan with device details, services, and HTTP request actions
    """
    try:
        # Retrieve deployment status with device information
        deployment_status = query_deployment_status(hours=1)
        devices = deployment_status.get("devices", [])
        
        # Filter devices for target zone and required services
        target_devices = [
            d for d in devices 
            if d.get("zone") == target_zone and 
               any(svc in d.get("services", []) for svc in required_services)
        ]
        
        if not target_devices:
            return {"error": f"No devices found in {target_zone} with services {required_services}"}
        
        # Get algorithm execution
        algorithm_result = await execute_algorithm(
            target_devices, algorithm
        )
        
        # Extract HTTP execution actions
        http_actions = generate_http_actions(
            target_devices, algorithm_result, algorithm
        )
        
        execution_plan = {
            "plan_id": plan_id,
            "timestamp": datetime.now().isoformat(),
            "target_zone": target_zone,
            "required_services": required_services,
            "algorithm": algorithm,
            
            # Device execution details
            "device_details": {
                "total_devices": len(target_devices),
                "devices": [
                    {
                        "id": d.get("device_id"),
                        "type": d.get("device_type"),
                        "location": d.get("location"),
                        "ip_address": d.get("ip_address"),
                    }
                    for d in target_devices
                ],
            },
            
            # Device services
            "device_services": {
                "protocol": target_devices[0].get("protocol", "MQTT") if target_devices else "MQTT",
                "resolution": "HD",  # Default resolution
                "services": list(set(
                    svc for d in target_devices for svc in d.get("services", [])
                    if svc in required_services
                )),
            },
            
            # Algorithm execution
            "sensor_activation": {
                "algorithm": algorithm,
                "selected_nodes": algorithm_result.get("selected_nodes", len(target_devices)),
                "execution_sequence": algorithm_result.get("sequence", []),
                "energy_efficiency": algorithm_result.get("energy_efficiency", 0),
            },
            
            # HTTP request execution actions
            "http_actions": http_actions,
        }
        
        logger.info(f"Plan {plan_id} executed: {len(target_devices)} devices, algorithm={algorithm}")
        return execution_plan
        
    except Exception as e:
        logger.error(f"Plan execution failed: {e}", exc_info=True)
        return {"error": str(e)}
