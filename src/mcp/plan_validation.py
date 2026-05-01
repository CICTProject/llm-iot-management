"""
Plan Validation: Validates orchestration plans against real-time deployment status and energy constraints for IoT sensor networks.

Key functionalities:
- Trade-off analysis between detection accuracy and energy consumption
- Adaptive recommendation engine for algorithm selection based on constraints
- Comprehensive reporting on validation results and recommendations
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

from src.utils.system import (
    query_deployment_status,
)

from src.utils.system import (
    execute_algorithm,
)

logger = logging.getLogger(__name__)

@mcp_server.tool(name="get_deployment_status")
async def get_deployment_status() -> Dict[str, Any]:
    """Get current deployment status for plan validation."""
    try:
        deployment_status = query_deployment_status()
        logger.info("Queried deployment status for validation")
        return deployment_status
    except Exception as e:
        logger.error(f"Failed to query deployment status for validation: {e}")
        return {"error": str(e)}

# Adaptive recommendation engine for algorithm selection based on user constraints
@mcp_server.tool(name="recommend_activation_algorithm")
async def recommend_activation_algorithm(
    devices: List[Dict[str, Any]],
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
        naive_result = await execute_algorithm(devices=devices,  algorithm="naive")
        sequential_result = await execute_algorithm(devices=devices, algorithm="sequential", activation_duration_seconds=activation_duration_seconds, zone_radius_meters=zone_radius_meters)
        probabilistic_result = await execute_algorithm(devices=devices, algorithm="probabilistic", target_position=target_position, elapsed_time_t=elapsed_time_t, t_base=t_base, r_min=r_min, r_max=r_max)
        
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