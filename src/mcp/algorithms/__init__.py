"""
WSN Sensor Activation Algorithms for IoT Deployment Plan Validation.

Implements energy-efficient sensor activation strategies:
- Algorithm 1.4.1: Naive Sensor Activation (Baseline)
- Algorithm 1.4.2: Sequential Zone-based Activation (Cellulaire)
- Algorithm 1.4.3: Probabilistic & Spatially Optimized Activation

These algorithms optimize power consumption and network lifetime
in wireless sensor network (WSN) deployments.
"""

from .naive import naive_sensor_activation
from .cellulaire import sequential_zone_activation
from .probabilistic import probabilistic_spatially_optimized_activation

__all__ = [
    "naive_sensor_activation",
    "sequential_zone_activation",
    "probabilistic_spatially_optimized_activation",
]
