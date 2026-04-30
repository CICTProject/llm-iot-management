# System-related tools for device registry and monitoring.
from typing import Any, Dict, List, Optional
from src.db.database import get_db_client
from src.db.models import DeviceType

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
