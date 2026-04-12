"""
Algorithm 1.3.2: Cellulaire Sequential Clustering Zone-based Activation.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Tuple

import numpy as np

from src.utils.energy import SensorNode, create_spatial_zones, serialize_zones

logger = logging.getLogger(__name__)


def sequential_zone_activation(
    nodes: List[SensorNode],
    activation_duration_seconds: int = 300,
    zone_radius_meters: float = 10.0,
) -> Dict[str, Any]:
    """
    Partitions sensor nodes into spatial zones using 3D clustering,
    then activates each zone sequentially for a fixed duration.
    Reduces simultaneous energy usage compared to naive approach.
    
    Args:
        nodes: List of sensor nodes representing the network
        activation_duration_seconds: Fixed duration for each node's active period (default 300s)
        zone_radius_meters: Radius for spatial zone clustering (default 10m)
        
    Returns:
        Dictionary containing:
            - algorithm: Algorithm identifier
            - description: Brief description of the algorithm
            - metrics: Performance metrics (energy, zones, efficiency)
            - zones: Spatial zone information and node distribution
            - activation_schedule: Detailed schedule for node activation
            - limitations: Known algorithm limitations
    """
    logger.info(f"Running Algorithm Sequential Zone Activation on {len(nodes)} nodes")
    logger.info(f"Zone radius: {zone_radius_meters}m, Activation duration: {activation_duration_seconds}s")
    
    # Phase 1: Spatial Clustering (partition nodes into zones)
    zones = create_spatial_zones(nodes, zone_radius_meters)
    logger.info(f"Partitioned {len(nodes)} nodes into {len(zones)} spatial zones")
    
    # Phase 2: Sequential Activation Schedule
    activation_schedule = []
    total_energy_saved = 0.0
    total_time_slots = len(zones)
    total_activation_events = 0
    total_transmission_events = 0.0
    
    for zone_idx, (zone_center, zone_nodes) in enumerate(zones.items()):
        slot_start = zone_idx * activation_duration_seconds
        
        for node in zone_nodes:
            if node.is_active:
                # Calculate energy cost: activation + transmission if event detected
                activation_cost = node.transmission_power * activation_duration_seconds / 3600.0  # Wh
                
                # Simulated event probability based on detection accuracy
                event_probability = node.detection_accuracy / 100.0
                transmission_cost = activation_cost * event_probability if event_probability > 0 else 0
                
                # Energy saved by not being active continuously
                continuous_energy = node.energy_consumption
                sequential_energy = min(activation_cost + transmission_cost, continuous_energy)
                energy_saved = max(0, continuous_energy - sequential_energy)
                
                activation_schedule.append({
                    "node_id": node.node_id,
                    "zone_center": zone_center,
                    "zone_index": zone_idx,
                    "time_slot": zone_idx,
                    "slot_start_seconds": slot_start,
                    "slot_end_seconds": slot_start + activation_duration_seconds,
                    "activation_duration_seconds": activation_duration_seconds,
                    "status": "SCHEDULED",
                    "coordinates": [node.x_coord, node.y_coord, node.z_coord],
                    "transmission_power_w": node.transmission_power,
                    "activation_energy_wh": activation_cost,
                    "transmission_probability": event_probability,
                    "sequential_energy_j": sequential_energy,
                    "continuous_energy_j": continuous_energy,
                    "energy_saved_j": energy_saved,
                    "signal_quality_dbm": node.signal_quality,
                    "detection_accuracy_percent": node.detection_accuracy,
                    "energy_remaining_percent": node.energy_remaining_percent,
                })
                total_energy_saved += energy_saved
                total_activation_events += 1
                if event_probability > 0:
                    total_transmission_events += event_probability
    
    # Calculate statistics
    total_nodes_energy = sum(n.energy_consumption for n in nodes)
    energy_efficiency = (total_energy_saved / total_nodes_energy * 100) if total_nodes_energy > 0 else 0.0
    avg_zone_size = len(nodes) / len(zones) if zones else 0
    total_cycle_time = total_time_slots * activation_duration_seconds
    
    metrics = {
        "algorithm": "sequential_zone_activation",
        "timestamp": datetime.now().isoformat(),
        "total_nodes": len(nodes),
        "total_zones": len(zones),
        "avg_nodes_per_zone": avg_zone_size,
        "activation_duration_seconds": activation_duration_seconds,
        "zone_radius_meters": zone_radius_meters,
        "total_cycle_time_seconds": total_cycle_time,
        "total_activation_events": total_activation_events,
        "total_transmission_events": round(total_transmission_events, 2),
        "total_energy_saved_j": total_energy_saved,
        "energy_efficiency_percent": energy_efficiency,
        "coverage_type": "zone_by_zone_sequential",
        "spatial_awareness": "3d_clustering",
    }
    
    logger.info(f"Algorithm complete: {len(zones)} zones, {energy_efficiency:.1f}% energy efficiency")
    
    return {
        "algorithm": "sequential_zone_activation",
        "name": "Sequential Zone Activation",
        "description": "Sequential activation by spatial zones reduces simultaneous energy usage while maintaining coverage",
        "metrics": metrics,
        "zones": serialize_zones(zones),
        "activation_schedule": activation_schedule,
        "limitations": [
            "High energy consumption as nodes activate even when unnecessary",
            "No awareness of event probability or real-time activity patterns",
            "Fixed activation time not adaptive to varying network conditions",
            "May miss events between zone activation windows",
            "Scalability depends on zone size and network density distribution",
        ],
    }
