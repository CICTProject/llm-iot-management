"""
MCP Server tools for IoT sensor network plan execution.

Implements 3 WSN sensor activation algorithms:
- Algorithm 1.3.1: Naive Sensor Activation (Baseline) - All devices activated simultaneously
- Algorithm 1.3.2: Cellulaire Sequential Clustering Zone-based Activation - Sequential zone-ordered activation
- Algorithm 1.3.3: Probabilistic & Spatially Optimized Activation - Temporal + spatial risk zone + metaheuristic optimization
"""

import logging
import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from . import mcp_server
from src.utils.energy import (
    check_compliance,
    parse_sensor_nodes_from_influxdb,
    evaluate_algorithm,
    select_best_algorithm,
    find_least_violating,
)
from src.db.database import get_db_client


from .algorithms import (
    naive_sensor_activation,
    sequential_zone_activation,
    probabilistic_spatially_optimized_activation,
)

logger = logging.getLogger(__name__)

# 1.3.1 Naive Sensor Activation Tool
@mcp_server.tool(name="execute_naive_activation")
async def execute_naive_sensor_activation() -> Dict[str, Any]:
    """
    Execute the naive sensor activation algorithm.
    Activates all nodes simultaneously for continuous monitoring.
    Baseline algorithm for comparison with optimized approaches.
    
    Returns:
        Validation report with activation plan and energy metrics
    """
    try:
        # Query IoT sensor data from InfluxDB
        db_client = get_db_client()
        query_api = db_client.get_query_client()
        
        query = '''
        from(bucket: "energy_consumption")
          |> range(start: -7d)
          |> filter(fn: (r) => r["_measurement"] == "iot_metrics")
        '''
        
        result = query_api.query(query)
        
        # Parse results into SensorNode objects
        nodes = parse_sensor_nodes_from_influxdb(result)
        
        if not nodes:
            logger.warning("No sensor nodes found in InfluxDB")
            return {
                "algorithm": "naive_sensor_activation",
                "error": "No sensor data available",
                "metrics": {"total_nodes": 0, "activated_nodes": 0},
            }
        
        # Run algorithm
        result = naive_sensor_activation(nodes)
        logger.info(f"Naive activation validation complete: {len(nodes)} nodes analyzed")
        return result
        
    except Exception as e:
        logger.error(f"Naive activation validation failed: {e}", exc_info=True)
        return {
            "algorithm": "naive_sensor_activation",
            "error": str(e),
            "metrics": {"total_nodes": 0, "activated_nodes": 0},
        }

# 1.3.2 Sequential Zone Activation Tool
@mcp_server.tool(name="execute_sequential_zone_activation")
async def execute_sequential_zone_activation(
    activation_duration_seconds: int = 300,
    zone_radius_meters: float = 10.0,
) -> Dict[str, Any]:
    """
    Execute the sequential zone activation algorithm.
    Activates nodes sequentially by spatial zones to reduce simultaneous energy use.
    
    Args:
        activation_duration_seconds: Duration each node stays active in a slot (default 300s)
        zone_radius_meters: Spatial radius for zone clustering (default 10m)
        
    Returns:
        Validation report with sequential schedule and zone analysis
    """
    try:
        # Query IoT sensor data from InfluxDB
        db_client = get_db_client()
        query_api = db_client.get_query_client()
        
        query = '''
        from(bucket: "energy_consumption")
          |> range(start: -7d)
          |> filter(fn: (r) => r["_measurement"] == "iot_metrics")
        '''
        
        result = query_api.query(query)
        
        # Parse results into SensorNode objects
        nodes = parse_sensor_nodes_from_influxdb(result)
        
        if not nodes:
            logger.warning("No sensor nodes found in InfluxDB")
            return {
                "algorithm": "sequential_zone_activation",
                "error": "No sensor data available",
                "metrics": {"total_nodes": 0, "total_zones": 0},
            }
        
        # Run algorithm
        result = sequential_zone_activation(
            nodes,
            activation_duration_seconds=activation_duration_seconds,
            zone_radius_meters=zone_radius_meters
        )
        
        logger.info(f"Sequential zone activation validation complete: {len(nodes)} nodes in {result['metrics']['total_zones']} zones")
        return result
        
    except Exception as e:
        logger.error(f"Sequential zone activation validation failed: {e}", exc_info=True)
        return {
            "algorithm": "sequential_zone_activation",
            "error": str(e),
            "metrics": {"total_nodes": 0, "total_zones": 0},
        }

# 1.3.3 Probabilistic & Spatially Optimized Activation Tool
@mcp_server.tool(name="execute_probabilistic_spatially_optimized_activation")
async def execute_probabilistic_spatially_optimized_activation(
    target_position: Optional[List[float]] = None,
    elapsed_time_t: float = 30.0,
    t_base: float = 20.0,
    r_min: float = 8.0,
    r_max: float = 35.0,
    sensing_radius: float = 12.0,
    num_risk_points: int = 120,
    epoch: int = 100,
    pop_size: int = 30,
) -> Dict[str, Any]:
    """
    Execute the probabilistic and spatially optimized activation algorithm.
    Combines temporal probability models with spatial risk zone analysis and
    metaheuristic optimization for minimal-cover sensor activation.
    
    Args:
        target_position: Event target coordinates [x, y, z] (default [50.0, 50.0, 25.0])
        elapsed_time_t: Time elapsed since reference point in seconds (default 30.0)
        t_base: Base activation duration in seconds (default 20.0)
        r_min: Minimum risk zone radius in meters (default 8.0)
        r_max: Maximum risk zone radius in meters (default 35.0)
        sensing_radius: Node sensing range in meters (default 12.0)
        num_risk_points: Number of sampled points for risk zone coverage (default 120)
        epoch: Optimization iterations (default 100)
        pop_size: Population size for whale optimization (default 30)
        
    Returns:
        Validation report with optimized sensor selection and activation plan
    """
    try:
        if target_position is None:
            target_position_tuple: Tuple[float, float, float] = (50.0, 50.0, 25.0)
        else:
            target_position_tuple = (
                float(target_position[0]),
                float(target_position[1]),
                float(target_position[2]),
            )
        
        # Query IoT sensor data from InfluxDB
        db_client = get_db_client()
        query_api = db_client.get_query_client()
        
        query = '''
        from(bucket: "energy_consumption")
          |> range(start: -7d)
          |> filter(fn: (r) => r["_measurement"] == "iot_metrics")
        '''
        
        result = query_api.query(query)
        
        # Parse results into SensorNode objects
        nodes = parse_sensor_nodes_from_influxdb(result)
        
        if not nodes:
            logger.warning("No sensor nodes found in InfluxDB")
            return {
                "algorithm": "probabilistic_spatially_optimized_activation",
                "error": "No sensor data available",
                "metrics": {"total_nodes": 0, "selected_nodes": 0},
            }
        
        # Run algorithm
        result = probabilistic_spatially_optimized_activation(
            nodes,
            target_position=target_position_tuple,
            elapsed_time_t=elapsed_time_t,
            t_base=t_base,
            r_min=r_min,
            r_max=r_max,
            sensing_radius=sensing_radius,
            num_risk_points=num_risk_points,
            epoch=epoch,
            pop_size=pop_size,
        )
        
        logger.info(f"Probabilistic activation validation complete: {len(nodes)} nodes analyzed, {result['metrics']['selected_nodes']} selected")
        return result
        
    except Exception as e:
        logger.error(f"Probabilistic spatially optimized activation validation failed: {e}", exc_info=True)
        return {
            "algorithm": "probabilistic_spatially_optimized_activation",
            "error": str(e),
            "metrics": {"total_nodes": 0, "selected_nodes": 0},
        }


# Adaptive recommendation engine for algorithm selection based on user constraints
@mcp_server.tool(name="recommend_activation_algorithm")
async def recommend_activation_algorithm(
    min_accuracy_percent: float = 80.0,
    max_energy_percent: float = 100.0,
    activation_duration_seconds: int = 300,
    zone_radius_meters: float = 10.0,
    target_position: Optional[List[float]] = None,
    elapsed_time_t: float = 30.0,
    t_base: float = 20.0,
    r_min: float = 8.0,
    r_max: float = 35.0,
) -> Dict[str, Any]:
    """
    Intelligent recommendation engine that adapts to user accuracy and energy constraints.
    
    Evaluates all 3 algorithms against user-defined constraints and recommends the
    optimal algorithm that best balances accuracy requirements with energy budgets.
    
    Args:
        min_accuracy_percent: Minimum acceptable detection accuracy [0-100] (default 80%)
        max_energy_percent: Maximum acceptable energy consumption level [0-100] (default 100%)
        activation_duration_seconds: Duration for sequential activation (default 300s)
        zone_radius_meters: Spatial clustering radius (default 10m)
        target_position: Event target [x, y, z] for probabilistic algorithm
        elapsed_time_t: Elapsed time for temporal model (default 30.0s)
        t_base: Base activation duration (default 20.0s)
        r_min: Minimum risk zone radius (default 8.0m)
        r_max: Maximum risk zone radius (default 35.0m)
        
    Returns:
        Recommendation report with:
        - User constraints and their interpretation
        - All 3 algorithms evaluated against constraints
        - Optimal algorithm recommendation
        - Trade-off analysis
        - Compliance report showing which algorithms meet requirements
    """
    try:
        logger.info(f"Starting adaptive recommendation: min_accuracy={min_accuracy_percent}%, max_energy={max_energy_percent}%")
        
        # Validate user inputs
        min_accuracy_percent = max(0, min(100, min_accuracy_percent))
        max_energy_percent = max(0, min(100, max_energy_percent))
        
        # Execute all 3 algorithms in parallel
        naive_result = await execute_naive_sensor_activation()
        sequential_result = await execute_sequential_zone_activation(
            activation_duration_seconds, zone_radius_meters
        )
        probabilistic_result = await execute_probabilistic_spatially_optimized_activation(
            target_position=target_position,
            elapsed_time_t=elapsed_time_t,
            t_base=t_base,
            r_min=r_min,
            r_max=r_max,
        )
        
        # Extract and evaluate metrics for each algorithm
        naive_eval = evaluate_algorithm(naive_result, "naive")
        seq_eval = evaluate_algorithm(sequential_result, "sequential")
        prob_eval = evaluate_algorithm(probabilistic_result, "probabilistic")
        
        # Check constraint compliance
        naive_compliant = check_compliance(naive_eval, min_accuracy_percent, max_energy_percent)
        seq_compliant = check_compliance(seq_eval, min_accuracy_percent, max_energy_percent)
        prob_compliant = check_compliance(prob_eval, min_accuracy_percent, max_energy_percent)
        
        # Find best recommendation
        compliant_algorithms = []
        if naive_compliant["meets_requirements"]:
            compliant_algorithms.append(("naive", naive_eval, naive_compliant))
        if seq_compliant["meets_requirements"]:
            compliant_algorithms.append(("sequential", seq_eval, seq_compliant))
        if prob_compliant["meets_requirements"]:
            compliant_algorithms.append(("probabilistic", prob_eval, prob_compliant))
        
        # Select best recommendation
        if compliant_algorithms:
            best_algo, best_eval, best_compliance = select_best_algorithm(compliant_algorithms)
            recommendation_status = "OPTIMAL_FOUND"
            recommendation_message = f"Recommended: {best_algo} - Meets all constraints with best overall balance"
        else:
            # Find least violating algorithm
            best_algo, best_eval, best_compliance = find_least_violating([
                ("naive", naive_eval, naive_compliant),
                ("sequential", seq_eval, seq_compliant),
                ("probabilistic", prob_eval, prob_compliant),
            ])
            recommendation_status = "COMPROMISED"
            recommendation_message = f"Recommended: {best_algo} - No algorithm meets all constraints, this offers best compromise"
        
        # Build comprehensive recommendation report
        recommendation = {
            "timestamp": datetime.now().isoformat(),
            "recommendation_type": "adaptive_accuracy_energy_aware",
            
            # User constraints summary
            "user_constraints": {
                "min_accuracy_percent": min_accuracy_percent,
                "max_energy_percent": max_energy_percent,
                "accuracy_interpretation": f"Accept at least {min_accuracy_percent}% detection accuracy",
                "energy_interpretation": f"Allow up to {max_energy_percent}% of maximum energy consumption",
            },
            
            # Algorithm evaluations
            "algorithms_evaluated": {
                "naive": {
                    "name": "Naive Sensor Activation (Baseline)",
                    "accuracy_percent": round(naive_eval["accuracy_percent"], 2),
                    "energy_percent": round(naive_eval["energy_percent"], 2),
                    "activated_nodes": naive_eval.get("activated_nodes", 0),
                    "compliance": {
                        "meets_accuracy": naive_compliant["meets_accuracy"],
                        "meets_energy": naive_compliant["meets_energy"],
                        "meets_requirements": naive_compliant["meets_requirements"],
                        "accuracy_margin": round(naive_compliant["accuracy_margin"], 2),
                        "energy_margin": round(naive_compliant["energy_margin"], 2),
                    },
                    "tradeoff_score": round(naive_eval["tradeoff_score"], 2),
                    "characteristics": {
                        "coverage": "Continuous global coverage",
                        "energy_strategy": "Maximum consumption - all nodes active",
                        "best_for": "Unlimited energy budget, maximum coverage needed",
                    }
                },
                "sequential": {
                    "name": "Sequential Zone Activation",
                    "accuracy_percent": round(seq_eval["accuracy_percent"], 2),
                    "energy_percent": round(seq_eval["energy_percent"], 2),
                    "zones_created": seq_eval.get("total_zones", 0),
                    "energy_saved_percent": round(seq_eval.get("energy_saved_percent", 0), 2),
                    "compliance": {
                        "meets_accuracy": seq_compliant["meets_accuracy"],
                        "meets_energy": seq_compliant["meets_energy"],
                        "meets_requirements": seq_compliant["meets_requirements"],
                        "accuracy_margin": round(seq_compliant["accuracy_margin"], 2),
                        "energy_margin": round(seq_compliant["energy_margin"], 2),
                    },
                    "tradeoff_score": round(seq_eval["tradeoff_score"], 2),
                    "characteristics": {
                        "coverage": "Zone-by-zone sequential coverage",
                        "energy_strategy": f"Moderate savings - sequential activation",
                        "best_for": "Moderate energy constraints, reasonable coverage continuity",
                    }
                },
                "probabilistic": {
                    "name": "Probabilistic & Spatially Optimized Activation",
                    "accuracy_percent": round(prob_eval["accuracy_percent"], 2),
                    "energy_percent": round(prob_eval["energy_percent"], 2),
                    "selected_nodes": prob_eval.get("selected_nodes", 0),
                    "optimization_method": "Whale Optimization Algorithm",
                    "compliance": {
                        "meets_accuracy": prob_compliant["meets_accuracy"],
                        "meets_energy": prob_compliant["meets_energy"],
                        "meets_requirements": prob_compliant["meets_requirements"],
                        "accuracy_margin": round(prob_compliant["accuracy_margin"], 2),
                        "energy_margin": round(prob_compliant["energy_margin"], 2),
                    },
                    "tradeoff_score": round(prob_eval["tradeoff_score"], 2),
                    "characteristics": {
                        "coverage": "Risk-zone aware minimal coverage",
                        "energy_strategy": "Optimized minimal selection - metaheuristic optimization",
                        "best_for": "Strict energy constraints, specific event targets, high accuracy needs",
                    }
                },
            },
            
            # Recommendation
            "recommendation": {
                "status": recommendation_status,
                "recommended_algorithm": best_algo,
                "message": recommendation_message,
                "expected_accuracy": round(best_eval["accuracy_percent"], 2),
                "expected_energy": round(best_eval["energy_percent"], 2),
                "tradeoff_balance": round(best_eval["tradeoff_score"], 2),
            },
            
            # Compliance report
            "compliance_summary": {
                "algorithms_meeting_requirements": len([a for a in [naive_compliant, seq_compliant, prob_compliant] if a["meets_requirements"]]),
                "total_algorithms": 3,
                "compliant_algorithms": [
                    name for name, _, comp in compliant_algorithms if comp["meets_requirements"]
                ],
            },
            
            # Decision guidance
            "decision_guidance": {
                "if_no_energy_constraint": "Use naive for maximum coverage",
                "if_moderate_energy_budget": "Use sequential for balanced approach",
                "if_strict_energy_budget": "Use probabilistic for optimized minimal coverage",
                "if_specific_event_location": "Use probabilistic with target_position parameter",
                "if_uncertain_about_constraints": f"Consider sequential as middle-ground option",
            },
        }
        
        logger.info(f"Recommendation complete: {best_algo} recommended with status={recommendation_status}")
        return recommendation
        
    except Exception as e:
        logger.error(f"Recommendation generation failed: {e}", exc_info=True)
        return {
            "error": str(e),
            "recommendation_type": "adaptive_accuracy_energy_aware",
            "status": "FAILED",
        }


