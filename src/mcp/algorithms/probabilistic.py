"""
Algorithm 1.3.3: Probabilistic & Spatially Optimized Activation.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Tuple

import numpy as np
from scipy.stats import gamma as gamma_dist
from sklearn.preprocessing import MinMaxScaler

try:
    from mealpy import BinaryVar, Problem
    from mealpy.swarm_based import WOA
    HAS_MEALPY = True
except ImportError:
    HAS_MEALPY = False

from src.utils.energy import SensorNode, create_spatial_zones

logger = logging.getLogger(__name__)


def normalize_node_features(nodes: List[SensorNode]) -> Dict[str, np.ndarray]:
    """
    Normalize sensor node features for scoring and optimization.
    
    Args:
        nodes: List of SensorNode objects
        
    Returns:
        Dictionary with normalized features
    """
    n = len(nodes)
    features = {
        "residual_energy": np.array([n.residual_energy for n in nodes]),
        "detection_accuracy": np.array([n.detection_accuracy for n in nodes]),
        "signal_strength": np.array([n.signal_strength for n in nodes]),
        "noise_level": np.array([n.noise_level for n in nodes]),
        "packet_loss_rate": np.array([n.packet_loss_rate for n in nodes]),
        "energy_consumption": np.array([n.energy_consumption for n in nodes]),
        "transmission_power": np.array([n.transmission_power for n in nodes]),
    }
    
    # Normalize each feature to [0, 1]
    scaler = MinMaxScaler()
    normalized = {}
    for key, values in features.items():
        if len(values) > 0 and np.ptp(values) > 0:  # ptp = peak-to-peak (max - min)
            normalized[f"{key}_norm"] = scaler.fit_transform(values.reshape(-1, 1)).flatten()
        else:
            normalized[f"{key}_norm"] = np.ones(n) * 0.5
    
    return normalized


def compute_gamma_t(elapsed_time: float, shape_k: float = 2.0, scale_theta: float = 10.0) -> float:
    """
    Temporal probability model: gamma(t) = P(T <= t) where T ~ Gamma(shape_k, scale_theta).
    
    Args:
        elapsed_time: Time elapsed since reference point
        shape_k: Gamma distribution shape parameter
        scale_theta: Gamma distribution scale parameter
        
    Returns:
        Probability in [0, 1]
    """
    gamma_t = gamma_dist.cdf(elapsed_time, a=shape_k, scale=scale_theta)
    return float(np.clip(gamma_t, 0.0, 1.0))


def compute_risk_radius(r_min: float, r_max: float, gamma_t: float) -> float:
    """
    Risk zone radius based on temporal probability.
    R = R_min + gamma(t) * (R_max - R_min)
    
    Args:
        r_min: Minimum risk zone radius
        r_max: Maximum risk zone radius
        gamma_t: Temporal probability factor in [0, 1]
        
    Returns:
        Risk zone radius
    """
    return float(r_min + gamma_t * (r_max - r_min))


def compute_distance_to_target(
    node_positions: np.ndarray,
    target_position: Tuple[float, float, float],
) -> np.ndarray:
    """
    Compute Euclidean distance from each node to target position.
    
    Args:
        node_positions: Array of shape (n_nodes, 3) with (x, y, z) coordinates
        target_position: Target position (xp, yp, zp)
        
    Returns:
        Array of distances
    """
    target = np.array(target_position, dtype=float)
    return np.linalg.norm(node_positions - target, axis=1)


def intersects_riskzone(
    distance_to_target: float,
    sensing_radius: float,
    risk_radius: float,
) -> bool:
    """
    Check if sensor coverage intersects risk zone.
    
    Args:
        distance_to_target: Distance from node to target
        sensing_radius: Node's sensing radius
        risk_radius: Risk zone radius
        
    Returns:
        True if coverage intersects risk zone
    """
    return distance_to_target <= (sensing_radius + risk_radius)


def select_candidate_nodes(
    nodes: List[SensorNode],
    target_position: Tuple[float, float, float],
    risk_radius: float,
    sensing_radius: float,
) -> List[SensorNode]:
    """
    Select candidate nodes whose coverage intersects risk zone.
    
    Args:
        nodes: All sensor nodes
        target_position: Target position
        risk_radius: Risk zone radius
        sensing_radius: Sensing range
        
    Returns:
        List of candidate nodes
    """
    positions = np.array([[n.x_coord, n.y_coord, n.z_coord] for n in nodes])
    distances = compute_distance_to_target(positions, target_position)
    
    candidates = []
    for node, dist in zip(nodes, distances):
        if intersects_riskzone(dist, sensing_radius, risk_radius):
            candidates.append(node)
    
    return candidates


def compute_node_quality_score(
    nodes: List[SensorNode],
    normalized: Dict[str, np.ndarray],
    weights: Dict[str, float],
) -> np.ndarray:
    """
    Compute quality score for each node based on normalized features.
    
    Args:
        nodes: List of sensor nodes
        normalized: Dictionary of normalized features
        weights: Feature weights
        
    Returns:
        Array of quality scores in [0, 1]
    """
    score = (
        weights.get("energy", 0.30) * normalized["residual_energy_norm"]
        + weights.get("accuracy", 0.25) * normalized["detection_accuracy_norm"]
        + weights.get("signal", 0.20) * normalized["signal_strength_norm"]
        - weights.get("noise", 0.10) * normalized["noise_level_norm"]
        - weights.get("packet_loss", 0.10) * normalized["packet_loss_rate_norm"]
        - weights.get("consumption", 0.05) * normalized["energy_consumption_norm"]
    )
    return np.clip(score, 0.0, 1.0)


def sample_riskzone_points(
    center: Tuple[float, float, float],
    radius: float,
    num_points: int,
    seed: int = 42,
) -> np.ndarray:
    """
    Sample points uniformly in risk zone sphere for coverage verification.
    
    Args:
        center: Risk zone center
        radius: Risk zone radius
        num_points: Number of sample points
        seed: Random seed
        
    Returns:
        Array of shape (num_points, 3) with sampled positions
    """
    rng = np.random.default_rng(seed)
    center = np.array(center, dtype=float)
    
    points = []
    while len(points) < num_points:
        candidate = rng.uniform(-radius, radius, size=3)
        if np.linalg.norm(candidate) <= radius:
            points.append(center + candidate)
    
    return np.array(points)


def build_coverage_matrix(
    node_positions: np.ndarray,
    risk_points: np.ndarray,
    sensing_radius: float,
) -> np.ndarray:
    """
    Build coverage matrix: coverage[i, j] = 1 if node i covers risk point j.
    
    Args:
        node_positions: Array of shape (n_candidates, 3)
        risk_points: Array of shape (n_risk_points, 3)
        sensing_radius: Node sensing range
        
    Returns:
        Coverage matrix of shape (n_candidates, n_risk_points)
    """
    dists = np.linalg.norm(
        node_positions[:, None, :] - risk_points[None, :, :],
        axis=2
    )
    return (dists <= sensing_radius).astype(int)


class MinimalCoverProblem(Problem):
    """
    Binary optimization problem for minimal set cover of risk zone.
    x[i] = 1 if candidate node i is selected.
    """

    def __init__(self, bounds=None, minmax="min", data=None, **kwargs):
        super().__init__(bounds=bounds, minmax=minmax, **kwargs)
        self.data = data

    def obj_func(self, x):
        if not HAS_MEALPY:
            return float(1e6)
        
        decoded = self.decode_solution(x)
        selected = np.array(decoded.get("device_selection", []), dtype=int)
        
        coverage_matrix = self.data["coverage_matrix"]
        energy_cost = self.data["energy_cost"]
        quality_reward = self.data["quality_reward"]
        
        alpha_num = self.data.get("alpha_num_active", 2.0)
        alpha_energy = self.data.get("alpha_energy_cost", 1.5)
        alpha_quality = self.data.get("alpha_quality_reward", 2.5)
        penalty_uncovered = self.data.get("penalty_uncovered", 1e6)
        penalty_no_sensor = self.data.get("penalty_no_sensor", 1e6)
        
        if selected.sum() == 0:
            return float(penalty_no_sensor)
        
        active_idx = np.where(selected == 1)[0]
        covered_points = coverage_matrix[active_idx].max(axis=0)
        n_uncovered = int((covered_points == 0).sum())
        
        fitness = (
            alpha_num * selected.sum()
            + alpha_energy * energy_cost[active_idx].sum()
            - alpha_quality * quality_reward[active_idx].sum()
        )
        
        if n_uncovered > 0:
            fitness += penalty_uncovered * n_uncovered
        
        return float(fitness)


def solve_minimal_cover(
    candidates: List[SensorNode],
    risk_points: np.ndarray,
    normalized: Dict[str, np.ndarray],
    cfg: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Solve minimal set cover using Whale Optimization Algorithm (WOA).
    
    Args:
        candidates: Candidate sensor nodes
        risk_points: Sampled risk zone points
        normalized: Normalized node features
        cfg: Configuration with optimization parameters
        
    Returns:
        Dictionary with selected devices and fitness
    """
    if not HAS_MEALPY:
        logger.warning("mealpy not installed, using greedy selection")
        # Fallback: greedy selection by quality score
        scores = normalized.get("detection_accuracy_norm", np.ones(len(candidates)))
        sorted_idx = np.argsort(-scores)
        selected_binary = np.zeros(len(candidates))
        selected_binary[sorted_idx[:max(1, len(candidates)//3)]] = 1
        selected_devices = [c for i, c in enumerate(candidates) if selected_binary[i] == 1]
        return {
            "selected_binary": selected_binary,
            "selected_devices": selected_devices,
            "best_fitness": 0.0,
            "coverage_matrix": None,
        }
    
    positions = np.array([[n.x_coord, n.y_coord, n.z_coord] for n in candidates])
    
    coverage_matrix = build_coverage_matrix(
        node_positions=positions,
        risk_points=risk_points,
        sensing_radius=cfg.get("sensing_radius", 12.0),
    )
    
    # Check if full coverage is possible
    impossible_mask = coverage_matrix.sum(axis=0) == 0
    if impossible_mask.any():
        n_impossible = int(impossible_mask.sum())
        logger.warning(f"Risk zone cannot be fully covered: {n_impossible} points uncovered")
    
    energy_cost = (
        0.60 * normalized.get("energy_consumption_norm", np.ones(len(candidates)))
        + 0.25 * (1.0 - normalized.get("residual_energy_norm", np.ones(len(candidates))))
        + 0.15 * normalized.get("transmission_power_norm", np.ones(len(candidates)))
    )
    
    quality_reward = (
        0.45 * normalized.get("detection_accuracy_norm", np.ones(len(candidates)))
        + 0.30 * normalized.get("signal_strength_norm", np.ones(len(candidates)))
        + 0.15 * (1.0 - normalized.get("noise_level_norm", np.ones(len(candidates))))
        + 0.10 * (1.0 - normalized.get("packet_loss_rate_norm", np.ones(len(candidates))))
    )
    
    data = {
        "coverage_matrix": coverage_matrix,
        "energy_cost": energy_cost,
        "quality_reward": quality_reward,
        "alpha_num_active": cfg.get("alpha_num_active", 2.0),
        "alpha_energy_cost": cfg.get("alpha_energy_cost", 1.5),
        "alpha_quality_reward": cfg.get("alpha_quality_reward", 2.5),
        "penalty_uncovered": cfg.get("penalty_uncovered", 1e6),
        "penalty_no_sensor": cfg.get("penalty_no_sensor", 1e6),
    }
    
    problem = MinimalCoverProblem(
        bounds=BinaryVar(n_vars=len(candidates), name="device_selection"),
        minmax="min",
        data=data,
        name="Minimal_Cover_RiskZone",
    )
    
    model = WOA.OriginalWOA(epoch=cfg.get("epoch", 100), pop_size=cfg.get("pop_size", 30))
    g_best = model.solve(problem, seed=cfg.get("seed", 42))
    
    selected_binary = problem.decode_solution(g_best.solution)["device_selection"]
    selected_binary = np.array(selected_binary, dtype=int)
    
    selected_devices = [c for i, c in enumerate(candidates) if selected_binary[i] == 1]
    
    return {
        "selected_binary": selected_binary,
        "selected_devices": selected_devices,
        "best_fitness": float(g_best.target.fitness),
        "coverage_matrix": coverage_matrix,
    }


def probabilistic_spatially_optimized_activation(
    nodes: List[SensorNode],
    target_position: Tuple[float, float, float] = (50.0, 50.0, 25.0),
    elapsed_time_t: float = 30.0,
    t_base: float = 20.0,
    r_min: float = 8.0,
    r_max: float = 35.0,
    sensing_radius: float = 12.0,
    gamma_shape_k: float = 2.0,
    gamma_scale_theta: float = 10.0,
    num_risk_points: int = 120,
    epoch: int = 100,
    pop_size: int = 30,
    seed: int = 42,
) -> Dict[str, Any]:
    """
    Probabilistic & Spatially Optimized Activation Algorithm (1.3.3).
    
    Adaptive sensor activation using:
    1. Temporal probability model (gamma distribution) for event risk
    2. Spatial risk zone identification
    3. Minimal set cover optimization with metaheuristic search (WOA)
    4. Quality-aware sensor selection balancing energy and detection accuracy
    
    Args:
        nodes: List of SensorNode objects
        target_position: Event target position (xp, yp, zp)
        elapsed_time_t: Time elapsed since reference point (seconds)
        t_base: Base activation duration (seconds)
        r_min: Minimum risk zone radius (meters)
        r_max: Maximum risk zone radius (meters)
        sensing_radius: Node sensing range (meters)
        gamma_shape_k: Gamma distribution shape parameter
        gamma_scale_theta: Gamma distribution scale parameter
        num_risk_points: Number of risk zone sample points for coverage
        epoch: Optimization epochs
        pop_size: Population size for WOA
        seed: Random seed
        
    Returns:
        Dictionary with algorithm results including selected devices and metrics
    """
    logger.info(f"Running Algorithm 1.3.3 Probabilistic & Spatially Optimized Activation")
    logger.info(f"Input: {len(nodes)} nodes, Target: {target_position}")
    
    if not nodes:
        raise ValueError("No sensor nodes provided")
    
    # Step 1: Temporal model - compute gamma(t)
    gamma_t = compute_gamma_t(elapsed_time_t, gamma_shape_k, gamma_scale_theta)
    logger.info(f"Temporal probability gamma(t): {gamma_t:.4f}")
    
    # Compute risk zone
    risk_radius = compute_risk_radius(r_min, r_max, gamma_t)
    risk_zone = {
        "center": target_position,
        "radius": risk_radius,
    }
    logger.info(f"Risk zone radius: {risk_radius:.2f}m")
    
    # Step 2: Select candidate nodes (coverage intersects risk zone)
    candidates = select_candidate_nodes(nodes, target_position, risk_radius, sensing_radius)
    if not candidates:
        raise ValueError("No candidate nodes intersect with risk zone")
    
    logger.info(f"Selected {len(candidates)} candidate nodes from {len(nodes)} total")
    
    # Normalize features
    normalized = normalize_node_features(candidates)
    
    # Compute quality scores
    weights = {
        "energy": 0.30,
        "accuracy": 0.25,
        "signal": 0.20,
        "noise": 0.10,
        "packet_loss": 0.10,
        "consumption": 0.05,
    }
    quality_scores = compute_node_quality_score(candidates, normalized, weights)
    
    # Step 3: Solve minimal cover using metaheuristic optimization
    cfg = {
        "sensing_radius": sensing_radius,
        "alpha_num_active": 2.0,
        "alpha_energy_cost": 1.5,
        "alpha_quality_reward": 2.5,
        "penalty_uncovered": 1e6,
        "penalty_no_sensor": 1e6,
        "epoch": epoch,
        "pop_size": pop_size,
        "seed": seed,
    }
    
    cover_result = solve_minimal_cover(candidates, 
                                       sample_riskzone_points(target_position, risk_radius, num_risk_points, seed),
                                       normalized, cfg)
    selected_devices = cover_result["selected_devices"]
    
    logger.info(f"Optimization selected {len(selected_devices)} active sensors")
    
    # Build activation plan
    activation_duration = t_base * gamma_t
    activation_plan = []
    total_energy = 0.0
    
    for node in selected_devices:
        energy_for_activation = node.transmission_power * activation_duration / 3600.0
        total_energy += energy_for_activation
        
        activation_plan.append({
            "node_id": node.node_id,
            "coordinates": [node.x_coord, node.y_coord, node.z_coord],
            "status": "ACTIVE_OPTIMIZED",
            "activation_duration_seconds": activation_duration,
            "transmission_power_w": node.transmission_power,
            "energy_for_activation_wh": energy_for_activation,
            "detection_accuracy_percent": node.detection_accuracy,
            "signal_quality_dbm": node.signal_quality,
            "energy_remaining_percent": node.energy_remaining_percent,
            "quality_score": float(quality_scores[candidates.index(node)] if node in candidates else 0.0),
        })
    
    metrics = {
        "algorithm": "probabilistic_spatially_optimized_activation",
        "timestamp": datetime.now().isoformat(),
        "temporal_probability_gamma_t": gamma_t,
        "risk_zone_radius_meters": risk_radius,
        "total_nodes": len(nodes),
        "candidate_nodes": len(candidates),
        "selected_nodes": len(selected_devices),
        "coverage_selection_efficiency": (len(selected_devices) / len(candidates) * 100) if candidates else 0.0,
        "activation_duration_seconds": activation_duration,
        "total_activation_energy_wh": total_energy,
        "best_optimization_fitness": cover_result["best_fitness"],
        "optimization_method": "whale_optimization_algorithm",
        "awareness_types": ["temporal", "spatial", "energy", "quality"],
    }
    
    logger.info(f"Algorithm complete: {len(selected_devices)} sensors activated, duration {activation_duration:.2f}s")
    
    return {
        "algorithm": "probabilistic_spatially_optimized_activation",
        "name": "Probabilistic & Spatially Optimized Activation (1.3.3)",
        "description": "Temporal probability + spatial risk zone + metaheuristic optimization for minimal energy, maximal detection accuracy",
        "metrics": metrics,
        "activation_plan": activation_plan,
        "limitations": [
            "Requires pre-defined target position for event prediction",
            "Optimization complexity increases with network size (binary problem NP-hard)",
            "Temporal model parameters (gamma shape/scale) must be tuned for specific environments",
            "Sensing radius must be known in advance",
            "WOA may not guarantee global optimum (metaheuristic limitation)",
        ],
    }
