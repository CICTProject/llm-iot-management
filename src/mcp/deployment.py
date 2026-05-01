"""
Deployment Monitoring: Provides tools for monitoring the overall deployment status, device details, and medical metrics in an IoT sensor network.

Key functionalities:
- Create comprehensive deployment status based on device registry and InfluxDB data
- Provide detailed device information and metrics for orchestration and validation agents
- Batch retrieval of medical metrics for multiple devices and metrics
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from . import mcp_server
from src.db.models import DeviceType

from src.utils.system import (
    get_device_from_registry,
    list_all_devices_from_registry,
    get_metric_readings,
    save_deployment_status,
    save_device_status,
    query_deployment_status,
)


logger = logging.getLogger(__name__)


@mcp_server.tool(name="create_deployment_status")
async def create_deployment_status() -> Dict[str, Any]:
    """
    Create and save comprehensive deployment status based on device registry.
    
    Returns:
        Deployment status object with all device details, metrics, and system health.
    """
    try:
        # Get all devices from registry
        devices = list_all_devices_from_registry()
        
        if not devices:
            logger.warning("No devices found in registry to create deployment status")
            return {"error": "No devices found in registry"}
        
        # Extract unique zones and services from devices
        zones = set()
        all_services = set()
        for device in devices:
            if device.get("zone"):
                zones.add(str(device.get("zone")))
            services = device.get("services", [])
            if isinstance(services, list):
                all_services.update(services)
        
        # Count device statuses
        online_count = len([d for d in devices if d.get("status") == "online"])
        offline_count = len([d for d in devices if d.get("status") == "offline"])
        error_count = len([d for d in devices if d.get("status") == "error"])
        
        # Create comprehensive deployment status
        deployment_status = {
            "deployment_id": "global",
            "timestamp": datetime.now().isoformat(),
            "deployment_mode": "INFLUXDB_MEDICAL",
            "total_devices": len(devices),
            "online": online_count,
            "offline": offline_count,
            "error": error_count,
            "zones": sorted(list(zones)),
            "services": sorted(list(all_services)),
            "active_alarms": 0,
            "active_plans": 0,
            "devices": [
                {
                    "device_id": d.get("device_id"),
                    "device_type": d.get("device_type"),
                    "zone": d.get("zone"),
                    "status": d.get("status"),
                    "battery_level": d.get("battery_level"),
                    "services": d.get("services", []),
                    "location": (d.get("x"), d.get("y"), d.get("z")) if d.get("x") else None,
                    "ip_address": d.get("ip_address"),
                    "protocol": d.get("protocol"),
                    "name": d.get("name"),
                }
                for d in devices
            ],
        }
        
        # Save comprehensive deployment status to InfluxDB
        save_deployment_status(deployment_status)
        
        # Also save individual device status records
        for device in devices:
            device_status = {
                "device_id": device.get("device_id"),
                "device_type": device.get("device_type"),
                "zone": device.get("zone"),
                "status": device.get("status"),
                "battery_level": device.get("battery_level"),
                "services": device.get("services", []),
                "location": (device.get("x"), device.get("y"), device.get("z")) if device.get("x") else None,
                "ip_address": device.get("ip_address"),
                "protocol": device.get("protocol"),
                "name": device.get("name"),
            }
            save_device_status(device_status)
        
        logger.info(f"Created deployment status with {len(devices)} devices, {online_count} online, {len(zones)} zones")
        return deployment_status
        
    except Exception as e:
        logger.error(f"Failed to create deployment status: {e}", exc_info=True)
        return {"error": str(e)}

# Device details and querying
@mcp_server.tool(name="get_device_details")
async def get_device_details(device_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific device.
    
    Args:
        device_id: Device identifier.
    
    Returns:
        Complete device configuration, status, location, and services.
    
    Raises:
        ValueError: If device not found.
    """
    device = get_device_from_registry(device_id)
    if not device:
        raise ValueError(f"Device {device_id} not found")
    return device


# Medical metric retrieval
@mcp_server.tool(name="read_medical_metric")
async def read_medical_metric(device_id: str, metric: str) -> Dict[str, Any]:
    """
    Read a medical metric from a sensor device.
    
    Args:
        device_id: Device identifier.
        metric: Metric name (e.g., heart_rate, spo2, ecg, body_temperature).
    
    Returns:
        Current metric value with unit, quality score, battery level, and timestamp.
    
    Raises:
        ValueError: If device or metric not found.
    """
    device = get_device_from_registry(device_id)
    if not device:
        raise ValueError(f"Device {device_id} not found")
    
    # Query latest reading from InfluxDB
    readings = get_metric_readings(device_id, metric, hours=24)
    if not readings:
        raise ValueError(f"No readings found for metric {metric} on device {device_id}")
    
    latest = readings[-1]  # Most recent
    
    return {
        "device_id": device_id,
        "metric": metric,
        "value": latest.get("value"),
        "unit": "units",
        "quality": latest.get("quality"),
        "battery_level": device.get("battery_level"),
        "timestamp": latest.get("timestamp"),
        "source": "influxdb",
    }


# Batch metric retrieval for multiple devices and metrics
@mcp_server.tool(name="read_multiple_medical_metrics")
async def read_multiple_medical_metrics(
    requests: List[Dict[str, str]],
) -> List[Dict[str, Any]]:
    """
    Read multiple medical metrics in batch from different devices.
    
    Args:
        requests: List of metric read requests with format
                 [{"device_id": "...", "metric": "..."}, ...].
    
    Returns:
        List of metric readings or error details for each request.
    """
    results = []
    for req in requests:
        device_id = req.get("device_id")
        metric = req.get("metric")
        try:
            if not device_id or not metric:
                raise ValueError("device_id and metric are required")
            result = await read_medical_metric(device_id, metric)
            results.append(result)
        except Exception as exc:
            results.append(
                {
                    "device_id": device_id,
                    "metric": metric,
                    "error": str(exc),
                }
            )
    return results


