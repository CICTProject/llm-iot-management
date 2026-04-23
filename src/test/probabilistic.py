
import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np
import pandas as pd

from src.utils.energy import SensorNode
from src.mcp.algorithms.probabilistic import probabilistic_spatially_optimized_activation

# Dataset loading and node construction
def load_sensornodes_from_csv(file_path: Path) -> List[SensorNode]:
    """
    Load sensor nodes from CSV and normalize coordinates to latent space [-1, 1].
    
    Sensor coordinates from Sensor_Energy_Consumption.csv are in real-world space.
    They are normalized to match hospital-movement latent coordinate space.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Sensor dataset not found: {file_path}")

    df = pd.read_csv(file_path)

    # Compute min/max for coordinate normalization to latent space [-1, 1]
    x_min, x_max = df["X_Coordinate"].min(), df["X_Coordinate"].max()
    y_min, y_max = df["Y_Coordinate"].min(), df["Y_Coordinate"].max()
    z_min, z_max = df["Z_Coordinate"].min(), df["Z_Coordinate"].max()

    nodes = []

    for i, row in df.iterrows():
        ts_value = row.get("Timestamp")
        timestamp = pd.to_datetime(ts_value, errors="coerce")
        if pd.isna(timestamp):
            timestamp = pd.Timestamp(datetime.utcnow())

        # Normalize coordinates from real-world space to latent space [-1, 1]
        x_normalized = 2.0 * (float(row.get("X_Coordinate", 0.0)) - x_min) / (x_max - x_min) - 1.0
        y_normalized = 2.0 * (float(row.get("Y_Coordinate", 0.0)) - y_min) / (y_max - y_min) - 1.0
        z_normalized = 2.0 * (float(row.get("Z_Coordinate", 0.0)) - z_min) / (z_max - z_min) - 1.0

        node = SensorNode(
            node_id=str(row.get("Node_ID", i)),
            timestamp=timestamp.to_pydatetime(),
            x_coord=x_normalized,
            y_coord=y_normalized,
            z_coord=z_normalized,
            initial_energy=float(row.get("Initial_Energy", 0.0)),
            residual_energy=float(row.get("Residual_Energy", 0.0)),
            transmission_power=float(row.get("Transmission_Power", 0.0)),
            signal_strength=float(row.get("Signal_Strength", 0.0)),
            noise_level=float(row.get("Noise_Level", 0.0)),
            energy_consumption=float(row.get("Energy_Consumption", 0.0)),
            packet_loss_rate=float(row.get("Packet_Loss_Rate", 0.0)),
            network_lifetime=int(row.get("Network_Lifetime", 0)),
            optimization_algorithm=str(row.get("Optimization_Algorithm", "unknown")),
            adaptive_learning_rate=float(row.get("Adaptive_Learning_Rate", 0.0)),
            temperature=float(row.get("Temperature", 0.0)),
            humidity=float(row.get("Humidity", 0.0)),
            detection_accuracy=float(row.get("Detection_Accuracy", 0.0)),
        )

        nodes.append(node)

    return nodes


def load_hcp_day(data_root: Path, day: int) -> pd.DataFrame:
    csv_path = data_root / "HCP_locations" / f"latent_positions_day_{day}.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"HCP file not found: {csv_path}")
    return pd.read_csv(csv_path)

def load_station_polygons(data_root: Path) -> pd.DataFrame:
    csv_path = data_root / "station_0ft.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Station file not found: {csv_path}")
    return pd.read_csv(csv_path)

def choose_best_time_slice(df: pd.DataFrame, requested_time: Optional[int] = None) -> int:
    if requested_time is not None:
        if requested_time not in set(df["time"].unique()):
            raise ValueError(f"Requested time={requested_time} is not present in the HCP file")
        return int(requested_time)

    counts = df.groupby("time")["ID"].nunique().sort_values(ascending=False)
    return int(counts.index[0])


def movement_centroid(day_df: pd.DataFrame, time_step: int) -> Tuple[float, float, float]:
    time_df = day_df[day_df["time"] == time_step]
    if time_df.empty:
        raise ValueError(f"No movement records found for time={time_step}")
    x = float(time_df["x"].mean())
    y = float(time_df["y"].mean())
    return (x, y, 0.0)


def station_center(stations_df: pd.DataFrame, station_id: int) -> Tuple[float, float, float]:
    station_points = stations_df[stations_df["station"] == station_id]
    if station_points.empty:
        raise ValueError(f"station={station_id} not found in station_0ft.csv")
    x = float(station_points["x"].mean())
    y = float(station_points["y"].mean())
    return (x, y, 0.0)


# Node construction from HCP positions
def build_nodes_from_time_slice(
    day_df: pd.DataFrame,
    time_step: int,
    sensing_radius: float,
    seed: int,
) -> List[SensorNode]:
    slice_df = day_df.loc[day_df["time"] == time_step, ["ID", "x", "y"]].copy()
    slice_df = slice_df.drop_duplicates(subset=["ID"]).sort_values("ID")
    if slice_df.empty:
        raise ValueError(f"No HCP positions found for time={time_step}")

    rng = np.random.default_rng(seed)
    nodes: List[SensorNode] = []

    for _, row in slice_df.iterrows():
        # Synthetic node features: reproducible, realistic ranges for testing.
        residual_energy = float(rng.uniform(0.45, 1.00))
        detection_accuracy = float(rng.uniform(72.0, 98.0))
        signal_strength = float(rng.uniform(-72.0, -38.0))  # dBm-like
        noise_level = float(rng.uniform(0.02, 0.25))
        packet_loss_rate = float(rng.uniform(0.00, 0.12))
        energy_consumption = float(rng.uniform(0.5, 2.5))   # arbitrary units
        transmission_power = float(rng.uniform(0.8, 4.5))   # watts

        nodes.append(
            SensorNode(
                node_id=f"HCP_{int(row['ID'])}",
                x_coord=float(row["x"]),
                y_coord=float(row["y"]),
                z_coord=0.0,
                residual_energy=residual_energy,
                detection_accuracy=detection_accuracy,
                signal_strength=signal_strength,
                noise_level=noise_level,
                packet_loss_rate=packet_loss_rate,
                energy_consumption=energy_consumption,
                transmission_power=transmission_power,
                sensing_radius=sensing_radius,
            )
        )

    return nodes

def main() -> None:
    parser = argparse.ArgumentParser(description="Test Algorithm 1.3.3 with HCP location data")
    parser.add_argument("--data-root", type=Path, default=Path("data"), help="Root folder containing Sensor_Energy_Consumption.csv and hospital-movement/")
    parser.add_argument("--day", type=int, default=2, choices=[2, 6, 7, 8, 9, 10], help="Dataset day to use")
    parser.add_argument("--time-step", type=int, default=None, help="Optional time slice from the HCP file; default selects the busiest time")
    parser.add_argument("--target-mode", type=str, default="hcp-centroid", choices=["hcp-centroid", "station"], help="Risk-zone center source")
    parser.add_argument("--station", type=int, default=12, help="Station id used only when --target-mode=station")
    parser.add_argument("--elapsed-time", type=float, default=30.0)
    parser.add_argument("--t-base", type=float, default=20.0)
    parser.add_argument("--r-min", type=float, default=0.10, help="Min risk radius in latent coordinate units")
    parser.add_argument("--r-max", type=float, default=0.40, help="Max risk radius in latent coordinate units")
    parser.add_argument("--sensing-radius", type=float, default=0.18, help="Sensor radius in latent coordinate units")
    parser.add_argument("--gamma-shape", type=float, default=2.0)
    parser.add_argument("--gamma-scale", type=float, default=10.0)
    parser.add_argument("--num-risk-points", type=int, default=120)
    parser.add_argument("--epoch", type=int, default=100)
    parser.add_argument("--pop-size", type=int, default=30)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output-json", type=Path, default=Path("results/algorithms/probabilistic_result.json"))
    args = parser.parse_args()

    movement_root = args.data_root / "hospital-movement"
    energy_csv = args.data_root / "Sensor_Energy_Consumption.csv"

    day_df = load_hcp_day(movement_root, args.day)

    time_step = choose_best_time_slice(day_df, args.time_step)
    if args.target_mode == "station":
        stations_df = load_station_polygons(movement_root)
        target_position = station_center(stations_df, args.station)
    else:
        target_position = movement_centroid(day_df, time_step)

    # Sensor nodes come from Sensor_Energy_Consumption.csv.
    nodes = load_sensornodes_from_csv(energy_csv)

    result = probabilistic_spatially_optimized_activation(
        nodes=nodes,
        target_position=target_position,
        elapsed_time_t=args.elapsed_time,
        t_base=args.t_base,
        r_min=args.r_min,
        r_max=args.r_max,
        sensing_radius=args.sensing_radius,
        gamma_shape_k=args.gamma_shape,
        gamma_scale_theta=args.gamma_scale,
        num_risk_points=args.num_risk_points,
        epoch=args.epoch,
        pop_size=args.pop_size,
        seed=args.seed,
    )

    # Add a bit of test metadata.
    result["test_context"] = {
        "dataset": "data/hospital-movement",
        "sensor_dataset": str(energy_csv),
        "day": args.day,
        "time_step": int(time_step),
        "num_input_nodes": len(nodes),
        "target_mode": args.target_mode,
        "target_station": args.station,
        "target_position": list(target_position),
        "latent_units_note": "x,y are latent coordinates in [-1,1], not meters",
    }

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    with args.output_json.open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print("=" * 80)
    print("Probabilistic & Spatially Optimized Algorithm Test completed")
    print("=" * 80)
    print(f"Dataset day              : {args.day}")
    print(f"Chosen time step         : {time_step}")
    print(f"Input HCP nodes          : {len(nodes)}")
    print(f"Target station           : {args.station}")
    print(f"Target position          : {target_position}")
    print(f"Selected nodes           : {result['metrics']['selected_nodes']}")
    print(f"Candidate nodes          : {result['metrics']['candidate_nodes']}")
    print(f"Risk radius              : {result['metrics']['risk_zone_radius_meters']:.6f}")
    print(f"Gamma(t)                 : {result['metrics']['temporal_probability_gamma_t']:.6f}")
    print(f"Activation duration (s)  : {result['metrics']['activation_duration_seconds']:.6f}")
    print(f"Total activation energy  : {result['metrics']['total_activation_energy_wh']:.6f}")
    print(f"Best fitness             : {result['metrics']['best_optimization_fitness']:.6f}")
    print(f"Output JSON              : {args.output_json.resolve()}")

    print("\nSelected activation plan preview:")
    for item in result.get("activation_plan", [])[:10]:
        print(
            f"  - {item['node_id']}: coord={item['coordinates']}, "
            f"quality={item['quality_score']:.4f}, energy_wh={item['energy_for_activation_wh']:.6f}"
        )


if __name__ == "__main__":
    main()
