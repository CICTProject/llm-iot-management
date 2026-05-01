"""
Algorithm 1.4.1: Naive Sensor Activation (Baseline).
"""

import logging
from datetime import datetime
from typing import Any, Dict, List

import numpy as np

from src.utils.energy import SensorNode

logger = logging.getLogger(__name__)


def naive_sensor_activation(nodes: List[SensorNode]) -> Dict[str, Any]:
    """
    Activates all sensor nodes simultaneously for continuous environmental monitoring.
    Each active node transmits data continuously at maximum transmission power.
    
    Args:
        nodes: List of SensorNode objects representing the network
        
    Returns:
        Dictionary containing:
            - algorithm: Algorithm identifier
            - description: Brief description of the algorithm
            - metrics: Performance metrics (energy, coverage, efficiency)
            - activation_plan: List of activated nodes with their config
            - limitations: Known algorithm limitations
    """
    logger.info(f"Running Algorithm Naive Sensor Activation on {len(nodes)} nodes")
    
    # Phase 1: Activate all nodes simultaneously
    activated_nodes = []
    total_energy_consumed = 0.0
    total_initial_energy = 0.0
    
    for node in nodes:
        setattr(node, "status", "active")
        activated_nodes.append({
            "node_id": node.node_id,
            "x_coord": node.x_coord,
            "y_coord": node.y_coord,
            "z_coord": node.z_coord,
            "initial_energy_j": node.initial_energy,
            "residual_energy_j": node.residual_energy,
            "transmission_power_w": node.transmission_power,
            "signal_quality_dbm": node.signal_strength,
            "detection_accuracy_percent": node.detection_accuracy,
        })
        total_energy_consumed += node.energy_consumption
        total_initial_energy += node.initial_energy
    
    # Calculate statistics
    activation_rate = len(activated_nodes) / len(nodes) * 100 if nodes else 0.0
    avg_energy_remaining = np.mean([n["residual_energy_j"] for n in activated_nodes]) if activated_nodes else 0.0
    avg_signal_quality = np.mean([n["signal_quality_dbm"] for n in activated_nodes]) if activated_nodes else 0.0
    total_transmission_power = sum(n["transmission_power_w"] for n in activated_nodes)
    energy_efficiency = total_energy_consumed / total_initial_energy * 100 if total_initial_energy > 0 else 0.0
    # Detection accuracy (Assuming continuous monitoring yields maximum accuracy)
    avg_detection_accuracy_percent = np.max([n["detection_accuracy_percent"] for n in activated_nodes]) if activated_nodes else 0.0

    metrics = {
        "algorithm": "naive_sensor_activation",
        "timestamp": datetime.now().isoformat(),
        "total_nodes": len(nodes),
        "activated_nodes": len(activated_nodes),
        "activation_rate_percent": activation_rate,
        "total_energy_consumed_j": total_energy_consumed,
        "total_initial_energy_j": total_initial_energy,
        "avg_energy_remaining_percent": avg_energy_remaining,
        "avg_signal_quality_dbm": avg_signal_quality,
        "total_transmission_power_w": total_transmission_power,
        "monitoring_coverage": "full_coverage",
        "redundancy_level": "maximum",
        "energy_efficiency_percent": energy_efficiency,
        "avg_detection_accuracy_percent": avg_detection_accuracy_percent,
    }
    
    logger.info(f"Algorithm complete: {len(activated_nodes)}/{len(nodes)} nodes activated")
    
    return {
        "algorithm": "naive_sensor_activation",
        "name": "Naive Sensor Activation (Baseline)",
        "description": "All devices activated for maximum monitoring (maximum coverage, high energy consumption)",
        "metrics": metrics,
        "activation_plan": activated_nodes,
        "limitations": [
            "High energy consumption due to full-coverage activation",
            "Redundant data transmission from overlapping coverage",
            "Shorter network lifetime due to rapid energy depletion",
            "Not suitable for energy-constrained deployments",
        ],
    }
