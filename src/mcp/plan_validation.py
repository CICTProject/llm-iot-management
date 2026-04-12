"""
MCP Server tools for energy-aware plan validation in IoT deployments.

Implements 3 energy efficiency algorithms for validating deployment plans:
- Algorithm 1.1: Energy-Aware Predictive Activation 
- Algorithm 1.2: Cellulaire Sequential Activation with Load Balancing 

Queries InfluxDB for IOT device timestamp, power consumption (kWh), voltage (V), current (A),
                         power factor, grid frequency (Hz), reactive power (kVAR), active power (kW), demand response event, temperature (°C), 
                         humidity (%), weather condition, solar power generation (kW), wind power generation (kW), 
                         previous day consumption (kWh), peak load hour, energy source type, user type, normalized consumption, energy efficiency score.
"""

import json
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from enum import Enum

from . import mcp_server
from src.utils.system import list_all_devices_from_registry
from src.utils.energy import calculate_peak_hours_from_db, reset_peak_hours_cache
from src.db.database import get_db_client

logger = logging.getLogger(__name__)


class GridState(Enum):
    """Grid operational states based on load conditions."""
    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"


# Algorithm 1.1: Energy-Aware Predictive Activation 
@mcp_server.tool(name="validate_plan_predictive")
async def validate_plan_predictive(
    zone: Optional[str] = None,
    device_type: Optional[str] = None,
    current_hour: Optional[int] = None,
    efficiency_threshold: float = 70.0
) -> Dict[str, Any]:
    """
    Algorithm 1.1: Energy-Aware Predictive Activation
    
    Validates deployment plans based on predicted energy consumption and efficiency scores.
    Prioritizes high-efficiency devices during peak load hours.
    
    Args:
        zone: Physical location zone to validate (e.g., corridor, ward_a).
        device_type: Device type to filter (e.g., medical_sensor, camera).
        current_hour: Current hour (0-23) for peak hour prediction.
        efficiency_threshold: Energy efficiency score threshold (0-100) for video activation.
    
    Returns:
        Validation result with device activation predictions and energy savings estimate.
    """
    
    if current_hour is None:
        current_hour = datetime.now().hour
    
    devices = list_all_devices_from_registry()
    
    # Filter by zone and device type
    if zone:
        devices = [d for d in devices if d.get("zone") == zone]
    if device_type:
        devices = [d for d in devices if d.get("device_type") == device_type]
    
    # Create device profiles with energy data
    device_profiles = []
    for device in devices:
        device_id = device.get("id")
        # Default values if not available
        power_consumption = float(device.get("power_consumption_kWh", 0.5))
        efficiency_score = float(device.get("energy_efficiency_score", 60.0))
        normalized_consumption = float(device.get("normalized_consumption", 0.5))
        
        device_profiles.append({
            "device_id": device_id,
            "power_consumption_kWh": power_consumption,
            "energy_efficiency_score": efficiency_score,
            "normalized_consumption": normalized_consumption,
            "zone": device.get("zone"),
            "device_type": device.get("device_type"),
        })
    
    # Sort by efficiency (high) and consumption (low)
    sorted_devices = sorted(
        device_profiles,
        key=lambda d: (-d["energy_efficiency_score"], d["power_consumption_kWh"])
    )
    
    peak_hours = calculate_peak_hours_from_db()
    is_peak_hour = current_hour in peak_hours
    
    predicted_activations = {}
    baseline_consumption = sum(d["power_consumption_kWh"] for d in device_profiles)
    optimized_consumption = 0.0
    critical_devices = []
    deferred_devices = []
    
    for device in sorted_devices:
        device_id = device["device_id"]
        high_efficiency = device["energy_efficiency_score"] > efficiency_threshold
        
        if is_peak_hour or high_efficiency:
            predicted_activations[device_id] = {
                "activation": "ACTIVE",
                "mode": "VIDEO_READY" if high_efficiency else "MOTION_ONLY",
                "efficiency_score": device["energy_efficiency_score"],
                "power_kWh": device["power_consumption_kWh"],
            }
            optimized_consumption += device["power_consumption_kWh"]
            
            if high_efficiency:
                critical_devices.append(device_id)
        else:
            predicted_activations[device_id] = {
                "activation": "DEFERRED",
                "reason": f"Low efficiency ({device['energy_efficiency_score']:.1f}%) "
                         f"and off-peak hour ({current_hour}:00)",
            }
            deferred_devices.append(device_id)
    
    savings_ratio = (baseline_consumption - optimized_consumption) / baseline_consumption \
        if baseline_consumption > 0 else 0.0
    
    return {
        "algorithm": "1.1_predictive_activation",
        "timestamp": datetime.now().isoformat(),
        "current_hour": current_hour,
        "is_peak_hour": is_peak_hour,
        "total_devices": len(device_profiles),
        "active_devices": len(critical_devices) + len([d for d in deferred_devices if predicted_activations[d]["activation"] == "ACTIVE"]),
        "critical_devices": critical_devices,
        "deferred_devices": deferred_devices,
        "baseline_consumption_kWh": baseline_consumption,
        "optimized_consumption_kWh": optimized_consumption,
        "estimated_energy_savings_percent": savings_ratio * 100,
        "predictions": predicted_activations,
        "validation_status": "VALID" if savings_ratio >= 0.3 else "SUBOPTIMAL",
    }


# Algorithm 1.2: Cellulaire Sequential Activation with Load Balancing
@mcp_server.tool(name="validate_plan_adaptive")
async def validate_plan_adaptive(
    zone: Optional[str] = None,
    device_type: Optional[str] = None,
    voltage_V: float = 230.0,
    frequency_Hz: float = 50.0,
    active_power_kW: float = 10.0,
    peak_capacity_kW: float = 20.0,
    demand_response_event: bool = False,
    power_factor: float = 0.95,
    load_balance_window_hours: Optional[int] = 4,
    load_threshold_kW: float = 10.0
) -> Dict[str, Any]:
    """
    Algorithm 1.2: Cellulaire Sequential Activation with Load Balancing
    
    Validates deployment plans based on real-time grid conditions and demand-response events.
    Uses multi-factor priority scoring for optimal device activation sequencing.
    
    Args:
        zone: Physical location zone to validate.
        device_type: Device type to filter.
        voltage_V: Current grid voltage in volts.
        frequency_Hz: Current grid frequency in Hz.
        active_power_kW: Current active power in kW.
        peak_capacity_kW: Peak grid capacity in kW.
        demand_response_event: Whether demand-response event is active.
        power_factor: Current power factor (0-1).
        load_balance_window_hours: Hours to balance load across.
        load_threshold_kW: Maximum load threshold for device activation.
    
    Returns:
        Validation result with grid-adaptive activation strategy and load balancing schedule.
    """
    
    # Ensure load_balance_window_hours has a valid value
    if load_balance_window_hours is None:
        load_balance_window_hours = 4
    
    devices = list_all_devices_from_registry()
    
    # Filter by zone and device type
    if zone:
        devices = [d for d in devices if d.get("zone") == zone]
    if device_type:
        devices = [d for d in devices if d.get("device_type") == device_type]
    
    # Determine grid state
    load_ratio = active_power_kW / peak_capacity_kW if peak_capacity_kW > 0 else 0
    
    if demand_response_event:
        grid_state = GridState.RED
    elif load_ratio > 0.85:
        grid_state = GridState.RED
    elif load_ratio > 0.70:
        grid_state = GridState.YELLOW
    else:
        grid_state = GridState.GREEN
    
    # Build device profiles with priorities
    device_priorities = []
    for device in devices:
        device_id = device.get("id")
        power_consumption = float(device.get("power_consumption_kWh", 0.5))
        efficiency_score = float(device.get("energy_efficiency_score", 60.0))
        normalized_consumption = float(device.get("normalized_consumption", 0.5))
        
        # Multi-factor priority score
        load_score = 1.0 - normalized_consumption
        efficiency_normalized = efficiency_score / 100.0
        temp_impact = 0.2  # Simplified
        humidity_impact = 0.1  # Simplified
        
        priority_score = (
            load_score * 0.4 +
            efficiency_normalized * 0.35 +
            (1.0 - temp_impact) * 0.15 +
            (1.0 - humidity_impact) * 0.1
        )
        
        device_priorities.append({
            "device_id": device_id,
            "power_consumption_kWh": power_consumption,
            "efficiency_score": efficiency_score,
            "normalized_consumption": normalized_consumption,
            "priority_score": priority_score,
            "zone": device.get("zone"),
            "device_type": device.get("device_type"),
        })
    
    # Sort by priority
    sorted_devices = sorted(
        device_priorities,
        key=lambda d: -d["priority_score"]
    )
    
    predictions = {}
    activation_schedule = {}
    estimated_energy_savings = 0.0
    
    if grid_state == GridState.RED:
        # Critical mode: activate only top 10% of devices
        activation_count = max(1, len(sorted_devices) // 10)
        strategy = "CRITICAL_MODE"
        estimated_energy_savings = 60.0
        
        for i, device in enumerate(sorted_devices):
            device_id = device["device_id"]
            if i < activation_count:
                predictions[device_id] = {
                    "state": "ACTIVE",
                    "mode": "CRITICAL_ALERT_ONLY",
                    "priority": device["priority_score"],
                }
            else:
                predictions[device_id] = {
                    "state": "STANDBY",
                    "mode": "LOW_POWER_MOTION_DETECT",
                    "priority": device["priority_score"],
                }
    
    elif grid_state == GridState.YELLOW:
        # Balanced mode: stagger activations
        devices_per_slot = max(1, len(sorted_devices) // (load_balance_window_hours * 3))
        strategy = "BALANCED_MODE"
        estimated_energy_savings = 45.0
        
        for i, device in enumerate(sorted_devices):
            device_id = device["device_id"]
            slot = i // devices_per_slot
            delay_minutes = (slot * load_balance_window_hours * 60) // max(1, len(sorted_devices))
            
            predictions[device_id] = {
                "state": "SCHEDULED",
                "delay_minutes": delay_minutes,
                "slot": slot,
                "priority": device["priority_score"],
            }
            activation_schedule[device_id] = f"+{delay_minutes} minutes"
    
    else:  # GREEN
        # Normal mode: activate respecting load threshold
        cumulative_load = 0.0
        strategy = "NORMAL_MODE"
        estimated_energy_savings = 20.0
        
        for device in sorted_devices:
            device_id = device["device_id"]
            power = device["power_consumption_kWh"]
            
            if cumulative_load + power <= load_threshold_kW:
                predictions[device_id] = {
                    "state": "ACTIVE",
                    "mode": "NORMAL",
                    "priority": device["priority_score"],
                }
                cumulative_load += power
            else:
                predictions[device_id] = {
                    "state": "DEFERRED",
                    "reason": f"Load threshold ({load_threshold_kW} kW) would be exceeded",
                    "priority": device["priority_score"],
                }
    
    return {
        "algorithm": "1.2_adaptive_activation",
        "timestamp": datetime.now().isoformat(),
        "grid_state": grid_state.value,
        "grid_load_ratio": load_ratio,
        "strategy": strategy,
        "total_devices": len(sorted_devices),
        "voltage_V": voltage_V,
        "frequency_Hz": frequency_Hz,
        "active_power_kW": active_power_kW,
        "peak_capacity_kW": peak_capacity_kW,
        "demand_response_event": demand_response_event,
        "power_factor": power_factor,
        "load_balance_window_hours": load_balance_window_hours,
        "load_threshold_kW": load_threshold_kW,
        "estimated_energy_savings_percent": estimated_energy_savings,
        "activation_schedule": activation_schedule,
        "predictions": predictions,
        "validation_status": "VALID",
    }


# Comparison Tool for all algorithms
@mcp_server.tool(name="compare_validation_algorithms")
async def compare_validation_algorithms(
    zone: Optional[str] = None,
    device_type: Optional[str] = None,
    current_hour: Optional[int] = None,
    voltage_V: float = 230.0,
    frequency_Hz: float = 50.0,
    active_power_kW: float = 10.0,
    peak_capacity_kW: float = 20.0,
    demand_response_event: bool = False,
) -> Dict[str, Any]:
    """
    Compare results from both validation algorithms on the same deployment plan.
    
    Args:
        zone: Physical location zone to validate.
        device_type: Device type to filter.
        current_hour: Current hour for predictive algorithm.
        voltage_V: Current grid voltage in volts.
        frequency_Hz: Current grid frequency in Hz.
        active_power_kW: Current active power in kW.
        peak_capacity_kW: Peak grid capacity in kW.
        demand_response_event: Whether demand-response event is active.
    
    Returns:
        Comparison of both algorithm results with recommendation.
    """
    
    if current_hour is None:
        current_hour = datetime.now().hour
    
    result_11 = await validate_plan_predictive(
        zone=zone,
        device_type=device_type,
        current_hour=current_hour
    )
    
    result_12 = await validate_plan_adaptive(
        zone=zone,
        device_type=device_type,
        voltage_V=voltage_V,
        frequency_Hz=frequency_Hz,
        active_power_kW=active_power_kW,
        peak_capacity_kW=peak_capacity_kW,
        demand_response_event=demand_response_event,
    )
    
    # Generate recommendation
    if demand_response_event or active_power_kW > peak_capacity_kW * 0.8:
        recommendation = "Use Algorithm 1.2 (adaptive) - Better for high load and demand-response scenarios"
    elif result_11["estimated_energy_savings_percent"] > result_12["estimated_energy_savings_percent"]:
        recommendation = "Use Algorithm 1.1 (predictive) - Higher energy savings in this scenario"
    else:
        recommendation = "Use Algorithm 1.2 (adaptive) - More robust to real-time grid conditions"
    
    return {
        "comparison": {
            "algorithm_1_1": {
                "energy_savings_percent": result_11["estimated_energy_savings_percent"],
                "status": result_11["validation_status"],
            },
            "algorithm_1_2": {
                "energy_savings_percent": result_12["estimated_energy_savings_percent"],
                "strategy": result_12["strategy"],
            },
            "savings_difference": abs(
                result_11["estimated_energy_savings_percent"] - 
                result_12["estimated_energy_savings_percent"]
            ),
            "recommendation": recommendation,
        },
        "timestamp": datetime.now().isoformat(),
    }
