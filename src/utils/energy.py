"""
Energy-related utility functions for plan validation and IoT sensor network analysis.

"""

import logging
import math
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from src.db.database import get_db_client

logger = logging.getLogger(__name__)



@dataclass
class SensorNode:
    """Represents an IoT sensor node in a wireless sensor network."""
    node_id: str
    timestamp: datetime
    x_coord: float
    y_coord: float
    z_coord: float
    initial_energy: float
    residual_energy: float
    transmission_power: float
    signal_strength: float
    noise_level: float
    energy_consumption: float 
    packet_loss_rate: float
    network_lifetime: int
    optimization_algorithm: str
    adaptive_learning_rate: float
    temperature: float
    humidity: float
    detection_accuracy: float
    
    @property
    def energy_remaining_percent(self) -> float:
        """Calculate remaining energy as percentage."""
        if self.initial_energy == 0:
            return 0.0
        return (self.residual_energy / self.initial_energy) * 100.0
    
    @property
    def is_active(self) -> bool:
        """Check if node has sufficient energy to operate."""
        return self.residual_energy > 0 and self.network_lifetime > 0
    
    @property
    def signal_quality(self) -> float:
        """Calculate signal quality metric (inverse of noise, weighted by strength)."""
        if self.noise_level == 0:
            return self.signal_strength
        return self.signal_strength / (1 + self.noise_level / 100.0)
    
    @property
    def spatial_distance(self) -> float:
        """Distance from origin in 3D space."""
        return math.sqrt(self.x_coord**2 + self.y_coord**2 + self.z_coord**2)


# IoT Sensor Network Utility Functions
def create_spatial_zones(
    nodes: List[SensorNode],
    zone_radius: float = 10.0,
) -> Dict[Tuple[float, float, float], List[SensorNode]]:
    """
    Partition nodes into spatial zones using 3D clustering.
    
    Uses distance-based clustering to group nearby nodes in 3D space.
    
    Args:
        nodes: List of sensor nodes
        zone_radius: Radius for zone clustering in meters
        
    Returns:
        Dictionary mapping zone centers (x, y, z) to lists of nodes in that zone
    """
    zones = {}
    unassigned = list(nodes)
    
    while unassigned:
        # Start new zone with first unassigned node
        zone_seed = unassigned[0]
        zone_center = (round(zone_seed.x_coord, 2), round(zone_seed.y_coord, 2), round(zone_seed.z_coord, 2))
        zone_nodes = []
        
        # Find all nodes within zone_radius in 3D space
        still_unassigned = []
        for node in unassigned:
            dist = math.sqrt(
                (node.x_coord - zone_seed.x_coord)**2 +
                (node.y_coord - zone_seed.y_coord)**2 +
                (node.z_coord - zone_seed.z_coord)**2
            )
            if dist <= zone_radius:
                zone_nodes.append(node)
            else:
                still_unassigned.append(node)
        
        zones[zone_center] = zone_nodes
        unassigned = still_unassigned
    
    return zones


def serialize_zones(zones: Dict[Tuple[float, float, float], List[SensorNode]]) -> Dict[str, dict]:
    """
    Serialize zones to JSON-compatible format.
    
    Args:
        zones: Dictionary of zone centers to node lists
        
    Returns:
        Serialized zones in JSON-compatible format
    """
    serialized = {}
    for center, nodes in zones.items():
        zone_key = f"zone_{len(serialized)}"
        serialized[zone_key] = {
            "center": {"x": center[0], "y": center[1], "z": center[2]},
            "node_count": len(nodes),
            "node_ids": [n.node_id for n in nodes],
            "avg_detection_accuracy": np.mean([n.detection_accuracy for n in nodes]) if nodes else 0.0,
            "total_transmission_power_w": sum(n.transmission_power for n in nodes),
        }
    return serialized


def parse_sensor_nodes_from_influxdb(query_result) -> List[SensorNode]:
    """
    Parse IoT sensor nodes from InfluxDB query result.
    
    Args:
        query_result: Result from InfluxDB query_api.query()
        
    Returns:
        List of SensorNode objects
    """
    nodes = []
    for table in query_result:
        for record in table.records:
            try:
                node = SensorNode(
                    node_id=record.tags.get("node_id", "unknown"),
                    timestamp=record.get_time(),
                    x_coord=float(record.values.get("x_coordinate", 0.0)),
                    y_coord=float(record.values.get("y_coordinate", 0.0)),
                    z_coord=float(record.values.get("z_coordinate", 0.0)),
                    initial_energy=float(record.values.get("initial_energy_j", 0.0)),
                    residual_energy=float(record.values.get("residual_energy_j", 0.0)),
                    transmission_power=float(record.values.get("transmission_power_w", 0.0)),
                    signal_strength=float(record.values.get("signal_strength_dbm", 0.0)),
                    noise_level=float(record.values.get("noise_level_db", 0.0)),
                    energy_consumption=float(record.values.get("energy_consumption_j", 0.0)),
                    packet_loss_rate=float(record.values.get("packet_loss_rate_percent", 0.0)),
                    network_lifetime=int(record.values.get("network_lifetime_seconds", 0)),
                    optimization_algorithm=record.tags.get("optimization_algorithm", "unknown"),
                    adaptive_learning_rate=float(record.values.get("adaptive_learning_rate", 0.0)),
                    temperature=float(record.values.get("temperature_c", 25.0)),
                    humidity=float(record.values.get("humidity_percent", 50.0)),
                    detection_accuracy=float(record.values.get("detection_accuracy_percent", 0.0)),
                )
                nodes.append(node)
            except Exception as e:
                logger.warning(f"Skipping malformed node record: {e}")
                continue
    
    return nodes

def evaluate_algorithm(result: Dict[str, Any], algo_type: str) -> Dict[str, float]:
    """Evaluate algorithm performance metrics."""
    metrics = result.get("metrics", {})
    
    # Extract metrics based on algorithm type
    if algo_type == "1.4.1_naive":
        accuracy_percent = 95.0  # Continuous monitoring = high accuracy
        energy_consumed = metrics.get("total_energy_consumed_j", 1000)
        activated_nodes = metrics.get("activated_nodes", 0)
    elif algo_type == "1.4.2_sequential":
        accuracy_percent = 75.0  # Zone-based = moderate accuracy
        energy_saved = metrics.get("total_energy_saved_j", 0)
        energy_consumed = metrics.get("total_energy_saved_j", 500)
        total_zones = metrics.get("total_zones", 1)
        activated_nodes = metrics.get("total_activation_events", 0)
    else:  # 1.4.3_probabilistic
        coverage_efficiency = metrics.get("coverage_selection_efficiency", 50)
        accuracy_percent = min(100, coverage_efficiency * 1.1)
        energy_consumed = metrics.get("total_activation_energy_wh", 300)
        selected_nodes = metrics.get("selected_nodes", 0)
        activated_nodes = selected_nodes
    
    # Normalize energy to 0-100 scale (lower is better)
    energy_normalized = min(100, (energy_consumed / 1000) * 100)
    
    # Trade-off score (40% energy + 60% accuracy)
    tradeoff_score = (100 - energy_normalized) * 0.4 + accuracy_percent * 0.6
    
    return {
        "accuracy_percent": accuracy_percent,
        "energy_percent": energy_normalized,
        "energy_saved_percent": energy_consumed / 1000 * 100 if algo_type != "1.4.1_naive" else 0,
        "tradeoff_score": tradeoff_score,
        "activated_nodes": activated_nodes,
        "total_zones": metrics.get("total_zones", 1),
        "selected_nodes": metrics.get("selected_nodes", 0),
    }


def check_compliance(eval_result: Dict, min_accuracy: float, max_energy: float) -> Dict[str, Any]:
    """Check if algorithm meets user constraints."""
    accuracy = eval_result["accuracy_percent"]
    energy = eval_result["energy_percent"]
    
    meets_accuracy = accuracy >= min_accuracy
    meets_energy = energy <= max_energy
    meets_requirements = meets_accuracy and meets_energy
    
    accuracy_margin = accuracy - min_accuracy  # Positive = exceeds minimum
    energy_margin = max_energy - energy  # Positive = within budget
    
    return {
        "meets_accuracy": meets_accuracy,
        "meets_energy": meets_energy,
        "meets_requirements": meets_requirements,
        "accuracy_margin": accuracy_margin,
        "energy_margin": energy_margin,
        "violations": [
            "Insufficient accuracy" if not meets_accuracy else None,
            "Exceeds energy budget" if not meets_energy else None,
        ]
    }


def select_best_algorithm(compliant_algorithms: List) -> Tuple:
    """Select best algorithm from compliant options (highest tradeoff score)."""
    return max(compliant_algorithms, key=lambda x: x[1]["tradeoff_score"])


def find_least_violating(all_algorithms: List) -> Tuple:
    """Find algorithm with least constraint violations."""
    def violation_score(item):
        algo_name, eval_result, compliance = item
        # Lower score = better (fewer violations)
        accuracy_violation = max(0, 80 - eval_result["accuracy_percent"])
        energy_violation = max(0, eval_result["energy_percent"] - 100)
        return accuracy_violation + energy_violation
    
    return min(all_algorithms, key=violation_score)




