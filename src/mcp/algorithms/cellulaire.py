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
    total_initial_energy = 0.0
    total_time_slots = len(zones)
    total_activation_events = 0
    total_transmission_events = 0.0
    total_sequential_energy = 0.0
    zone_accuracy_averages = []  # Track average detection accuracy per zone
    
    for zone_idx, (zone_center, zone_nodes) in enumerate(zones.items()):
        slot_start = zone_idx * activation_duration_seconds
        
        
        for node in zone_nodes:
            node.status = "active"  # Mark node as scheduled for activation
            if node.status == "active":
                # Sequential energy: node active for only 1 out of total_time_slots
                sequential_energy_j = node.energy_consumption * activation_duration_seconds / 3600.0  
                
                # Continuous energy: if node were active for entire cycle
                continuous_energy_j = node.energy_consumption * total_time_slots / 3600.0
                
                # Energy saved by sequential activation vs continuous
                energy_saved = max(0, continuous_energy_j - sequential_energy_j)
                
                # Detection accuracy is assumed to be proportional to signal quality and active time
                detection_accuracy = node.detection_accuracy * (activation_duration_seconds / (total_time_slots * activation_duration_seconds))

                activation_schedule.append({
                    "node_id": node.node_id,
                    "zone_center": zone_center,
                    "zone_index": zone_idx,
                    "time_slot": zone_idx,
                    "slot_start_seconds": slot_start,
                    "slot_end_seconds": slot_start + activation_duration_seconds,
                    "activation_duration_seconds": activation_duration_seconds,
                    "coordinates": [node.x_coord, node.y_coord, node.z_coord],
                    "transmission_power_w": node.transmission_power,
                    "activation_energy_wh": sequential_energy_j / 3600.0,
                    "sequential_energy_j": sequential_energy_j,
                    "continuous_energy_j": continuous_energy_j,
                    "energy_saved_j": energy_saved,
                    "signal_quality_dbm": node.signal_quality,
                    "detection_accuracy_percent": detection_accuracy,
                    "energy_remaining_percent": node.energy_remaining_percent,
                })
                total_energy_saved += energy_saved
                total_activation_events += 1
                total_sequential_energy += sequential_energy_j
                if detection_accuracy > 0:
                    total_transmission_events += 1
                total_initial_energy += node.initial_energy
 
        
        # Detection accuracy reduced by off time fraction
        time_active_fraction = activation_duration_seconds / total_time_slots if total_time_slots > 0 else 0
        avg_detection_accuracy_zones = np.mean([n.detection_accuracy * time_active_fraction for n in zone_nodes]) if zone_nodes else 0.0        
        zone_accuracy_averages.append(avg_detection_accuracy_zones)  # Collect zone average        
        logger.info(f"Zone {zone_idx}: {len(zone_nodes)} nodes, Avg detection accuracy: {avg_detection_accuracy_zones:.2f}%, Energy saved: {energy_saved:.6f} J")
    
    # Calculate statistics
    avg_zone_size = len(nodes) / len(zones) if zones else 0
    
    # Calculate total continuous energy baseline (if all nodes active entire cycle)
    total_continuous_energy = sum(n.energy_consumption * total_time_slots / 3600.0 for n in nodes)
    
    # Calculate total sequential energy (if each node active for only 1 slot)
    total_sequential_energy = total_continuous_energy * activation_duration_seconds / 3600.0 if total_time_slots > 0 else 0
    
    # Energy efficiency: savings vs continuous baseline
    energy_efficiency = (total_energy_saved / total_continuous_energy * 100) if total_continuous_energy > 0 else 0.0
    
    # Average detection accuracy across all zones (reduced by off time)
    avg_detection_accuracy_percent = np.mean(zone_accuracy_averages) if zone_accuracy_averages else 0.0
    

    metrics = {
        "algorithm": "sequential_zone_activation",
        "timestamp": datetime.now().isoformat(),
        "total_nodes": len(nodes),
        "total_zones": len(zones),
        "avg_nodes_per_zone": avg_zone_size,
        "activation_duration_seconds": activation_duration_seconds,
        "zone_radius_meters": zone_radius_meters,
        "total_nodes_energy_j": total_continuous_energy,
        "total_continuous_energy_j": total_continuous_energy,
        "total_sequential_energy_j": total_sequential_energy,
        "total_transmission_events": round(total_transmission_events, 2),
        "total_energy_saved_j": total_energy_saved,
        "energy_efficiency_percent": energy_efficiency,
        "avg_detection_accuracy_percent": avg_detection_accuracy_percent,
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
