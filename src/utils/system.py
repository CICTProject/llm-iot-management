# System-related tools for device registry and monitoring.
from datetime import datetime
import json
from typing import Any, Dict, List, Optional
from src.db.database import get_db_client
from src.db.models import DeviceType
from influxdb_client.client.write_api import SYNCHRONOUS, Point

import logging

logger = logging.getLogger(__name__)

def get_device_from_registry(device_id: str) -> Optional[Dict[str, Any]]:
    """Query device registry from InfluxDB."""
    db_client = get_db_client()
    query_api = db_client.get_query_client()
    
    query = f'''
        from(bucket: "{db_client.bucket}")
            |> range(start: -30d)
            |> filter(fn: (r) => r._measurement == "device_registry")
            |> filter(fn: (r) => r.device_id == "{device_id}")
            |> last()
    '''
    
    try:
        result = query_api.query(query)
        if result and len(result) > 0:
            records = result[0].records
            if records:
                record = records[0]
                return {
                    "device_id": record.values.get("device_id"),
                    "device_type": record.values.get("device_type"),
                    "name": record.values.get("name"),
                    "status": record.values.get("status"),
                    "ip_address": record.values.get("ip_address"),
                    "battery_level": record.values.get("battery_level"),
                    "protocol": record.values.get("protocol"),
                }
        return None
    except Exception as e:
        logger.error("Error querying device registry: %s", e)
        return None


def list_all_devices_from_registry() -> List[Dict[str, Any]]:
    """Query all devices from InfluxDB registry."""
    db_client = get_db_client()
    query_api = db_client.get_query_client()
    
    query = f'''
        from(bucket: "{db_client.bucket}")
            |> range(start: -30d)
            |> filter(fn: (r) => r._measurement == "device_registry")
            |> last()
    '''
    
    devices = []
    try:
        result = query_api.query(query)
        if result:
            for table in result:
                for record in table.records:
                    devices.append({
                        "device_id": record.values.get("device_id"),
                        "device_type": record.values.get("device_type"),
                        "protocol": record.values.get("protocol"),
                        "zone": record.values.get("zone"),
                        "name": record.values.get("name"),
                        "status": record.values.get("status"),
                        "ip_address": record.values.get("ip_address"),
                        "battery_level": record.values.get("battery_level"),
                        "services_count": record.values.get("services_count", 0),
                    })
    except Exception as e:
        logger.error("Error querying device registry: %s", e)
    
    return devices


def get_metric_readings(
    device_id: str, 
    metric: Optional[str] = None,
    hours: int = 24,
) -> List[Dict[str, Any]]:
    """Query metric readings from InfluxDB."""
    db_client = get_db_client()
    query_api = db_client.get_query_client()
    
    metric_filter = f'|> filter(fn: (r) => r.metric == "{metric}")' if metric else ''
    
    query = f'''
        from(bucket: "{db_client.bucket}")
            |> range(start: -{hours}h)
            |> filter(fn: (r) => r._measurement == "medical_reading")
            |> filter(fn: (r) => r.device_id == "{device_id}")
            {metric_filter}
    '''
    
    readings = []
    try:
        result = query_api.query(query)
        if result:
            for table in result:
                for record in table.records:
                    readings.append({
                        "device_id": device_id,
                        "metric": record.values.get("metric"),
                        "value": record.values.get("_value"),
                        "quality": record.values.get("quality"),
                        "timestamp": record.get_time().isoformat() if record.get_time() else None,
                    })
    except Exception as e:
        logger.error("Error querying readings: %s", e)
    
    return readings

def generate_activation_sequence(devices: List[Dict[str, Any]], services: List[str]) -> List[Dict[str, Any]]:
    """
    Generate device activation sequence based on device hierarchy and dependencies.
    
    Args:
        devices: List of devices to activate.
        services: Required services list.
    
    Returns:
        Ordered activation sequence with timing and dependencies.
    """
    sequence = []
    
    # Sort devices: gateways first, then edge nodes, then endpoints
    device_type_order = {
        DeviceType.GATEWAY.value: 0,
        DeviceType.EDGE_NODE.value: 1,
        DeviceType.MEDICAL_SENSOR.value: 2,
        DeviceType.CAMERA.value: 3,
    }
    
    sorted_devices = sorted(
        devices,
        key=lambda d: device_type_order.get(d.get("device_type"), 99)
    )
    
    for idx, device in enumerate(sorted_devices):
        sequence.append({
            "order": idx + 1,
            "device_id": device.get("device_id"),
            "device_type": device.get("device_type"),
            "delay_seconds": idx * 2,  # Stagger activation
            "dependencies": [sorted_devices[i].get("device_id") for i in range(idx)],
        })
    
    return sequence

# Deployment status management functions
def save_deployment_status(deployment_status: Dict[str, Any]) -> None:
    """
    Save comprehensive deployment status to InfluxDB deployment_status bucket.
    
    Saves complete deployment state including all device information, zones,
    services, statuses, and metadata for use by orchestration and validation agents.
    
    Args:
        deployment_status: Dict containing:
            - deployment_id: Unique deployment identifier
            - timestamp: ISO format timestamp
            - deployment_mode: Operating mode (INFLUXDB_MEDICAL, etc.)
            - total_devices: Total device count
            - online: Count of online devices
            - offline: Count of offline devices
            - error: Count of devices in error state
            - zones: List of zones in deployment
            - services: List of available services
            - devices: List of device info dicts with all details
            - active_plans: Number of active orchestration plans
    """
    try:
        db_client = get_db_client()
        write_api = db_client.get_write_api()
        
        # Build comprehensive deployment status point with all device information
        point = Point("deployment_state") \
            .tag("deployment_id", deployment_status.get("deployment_id", "global")) \
            .tag("deployment_mode", deployment_status.get("deployment_mode", "INFLUXDB_MEDICAL")) \
            .field("total_devices", deployment_status.get("total_devices", 0)) \
            .field("online_devices", deployment_status.get("online", 0)) \
            .field("offline_devices", deployment_status.get("offline", 0)) \
            .field("error_devices", deployment_status.get("error", 0)) \
            .field("active_plans", deployment_status.get("active_plans", 0)) \
            .field("num_zones", len(deployment_status.get("zones", []))) \
            .field("num_services", len(deployment_status.get("services", []))) \
            .field("status_data", json.dumps({
                "deployment_id": deployment_status.get("deployment_id", "global"),
                "timestamp": deployment_status.get("timestamp", datetime.now().isoformat()),
                "deployment_mode": deployment_status.get("deployment_mode", "INFLUXDB_MEDICAL"),
                "total_devices": deployment_status.get("total_devices", 0),
                "online": deployment_status.get("online", 0),
                "offline": deployment_status.get("offline", 0),
                "error": deployment_status.get("error", 0),
                "zones": deployment_status.get("zones", []),
                "services": deployment_status.get("services", []),
                "active_alarms": deployment_status.get("active_alarms", 0),
                "active_plans": deployment_status.get("active_plans", 0),
                "devices": [
                    {
                        "device_id": d.get("device_id"),
                        "device_type": d.get("device_type"),
                        "zone": d.get("zone"),
                        "status": d.get("status"),
                        "battery_level": d.get("battery_level"),
                        "services": d.get("services", []),
                        "location": d.get("location"),
                        "ip_address": d.get("ip_address"),
                        "protocol": d.get("protocol"),
                        "name": d.get("name"),
                    }
                    for d in deployment_status.get("devices", [])
                ],
            })) \
            .time(datetime.now())
        
        write_api.write(bucket="deployment_status", record=point)
        logger.info(f"Deployment status saved: {deployment_status.get('total_devices', 0)} devices, "
                   f"{deployment_status.get('online', 0)} online, {len(deployment_status.get('zones', []))} zones")
    except Exception as e:
        logger.error(f"Failed to save deployment status to InfluxDB: {e}", exc_info=True)


def save_device_status(device_info: Dict[str, Any]) -> None:
    """
    Save comprehensive individual device status to InfluxDB deployment_status bucket.
    
    Saves detailed device information including type, zone, location, services,
    battery level, and all metadata for device orchestration and monitoring.
    
    Args:
        device_info: Dict containing:
            - device_id: Unique device identifier
            - device_type: Type of device (gateway, edge_node, medical_sensor, camera)
            - zone: Physical location zone
            - status: Current device status (online, offline, error)
            - battery_level: Battery level percentage
            - services: List of services this device provides
            - location: (x, y, z) coordinates or similar
            - ip_address: Device IP address
            - protocol: Communication protocol (MQTT, HTTP, etc.)
            - name: Human-readable device name
    """
    try:
        db_client = get_db_client()
        write_api = db_client.get_write_api()
        
        point = Point("device_status") \
            .tag("device_id", device_info.get("device_id", "unknown")) \
            .tag("device_type", device_info.get("device_type", "unknown")) \
            .tag("zone", device_info.get("zone", "unknown")) \
            .tag("status", device_info.get("status", "unknown")) \
            .field("battery_level", float(device_info.get("battery_level", 0))) \
            .field("num_services", len(device_info.get("services", []))) \
            .field("device_data", json.dumps({
                "device_id": device_info.get("device_id"),
                "device_type": device_info.get("device_type"),
                "zone": device_info.get("zone"),
                "status": device_info.get("status"),
                "battery_level": device_info.get("battery_level"),
                "services": device_info.get("services", []),
                "location": device_info.get("location"),
                "ip_address": device_info.get("ip_address"),
                "protocol": device_info.get("protocol"),
                "name": device_info.get("name"),
            })) \
            .time(datetime.now())
        
        write_api.write(bucket="deployment_status", record=point)
        logger.debug(f"Device status saved: {device_info.get('device_id')} ({device_info.get('status')})")
    except Exception as e:
        logger.error(f"Failed to save device status to InfluxDB: {e}", exc_info=True)


def query_deployment_status(hours: int = 1) -> Dict[str, Any]:
    """
    Query comprehensive deployment status from InfluxDB deployment_status bucket.
    
    Retrieves the most recent deployment state snapshot including all device
    information, zones, services, and deployment metrics for orchestration and
    validation agents.
    
    Args:
        hours: Time range in hours to query (default 1 hour)
    
    Returns:
        Complete deployment status dict with all device details, zones, services,
        device counts, and current states.
    """
    try:
        db_client = get_db_client()
        query_api = db_client.get_query_client()
        
        query = f'''
        from(bucket: "deployment_status")
          |> range(start: -{hours}h)
          |> filter(fn: (r) => r["_measurement"] == "deployment_state")
          |> group(columns: ["deployment_id"])
          |> last()
        '''
        
        result = query_api.query(query)
        
        status_list = []
        for table in result:
            for record in table.records:
                status_json = record.values.get("status_data")
                if status_json:
                    try:
                        status_dict = json.loads(status_json)
                        status_list.append(status_dict)
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to decode deployment status JSON")
        
        # Return the most recent status with all device information
        if status_list:
            latest_status = status_list[0]
            logger.info(f"Retrieved deployment status: {latest_status.get('total_devices', 0)} devices, "
                       f"{latest_status.get('online', 0)} online")
            return latest_status
        
        return {
            "deployment_id": "global",
            "timestamp": datetime.now().isoformat(),
            "total_devices": 0,
            "devices": [],
            "zones": [],
            "services": [],
            "error": "No deployment status available",
        }
    except Exception as e:
        logger.error(f"Failed to query deployment status from InfluxDB: {e}", exc_info=True)
        return {}


# Orchestration plan management functions
def save_orchestration_plan(plan: Dict[str, Any]) -> None:
    """Save orchestration plan to InfluxDB orchestration_plans bucket."""
    try:
        db_client = get_db_client()
        write_api = db_client.get_write_api(write_points=SYNCHRONOUS)
                
        point = Point("orchestration_plan") \
            .tag("plan_id", plan.get("plan_id", "unknown")) \
            .tag("target_zone", plan.get("target_zone", "unknown")) \
            .field("plan_data", json.dumps(plan)) \
            .time(datetime.now())
        
        write_api.write(bucket="orchestration_plans", record=point)
        logger.info(f"Orchestration plan {plan.get('plan_id', 'unknown')} saved to InfluxDB")
    except Exception as e:
        logger.error(f"Failed to save orchestration plan to InfluxDB: {e}")