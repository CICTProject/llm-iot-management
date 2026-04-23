import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np
import pandas as pd

from src.utils.energy import SensorNode
from src.mcp.algorithms.cellulaire import sequential_zone_activation

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


def main() -> None:
    parser = argparse.ArgumentParser(description="Test Algorithm 1.3.2 Sequential Zone-based Activation")
    parser.add_argument("--data-root", type=Path, default=Path("data"), help="Root folder containing Sensor_Energy_Consumption.csv")
    parser.add_argument("--activation-duration", type=int, default=300, help="Duration per zone activation in seconds")
    parser.add_argument("--zone-radius", type=float, default=0.2, help="Zone radius in latent coordinate units")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--output-json", type=Path, default=Path("results/algorithms/cellulaire_result.json"))
    args = parser.parse_args()

    energy_csv = args.data_root / "Sensor_Energy_Consumption.csv"

    # Sensor nodes from Sensor_Energy_Consumption.csv
    nodes = load_sensornodes_from_csv(energy_csv)
    
    np.random.seed(args.seed)

    result = sequential_zone_activation(
        nodes=nodes,
        activation_duration_seconds=args.activation_duration,
        zone_radius_meters=args.zone_radius,
    )

    # Add test metadata
    result["test_context"] = {
        "sensor_dataset": str(energy_csv),
        "num_input_nodes": len(nodes),
        "algorithm": "1.3.2_cellulaire",
        "description": "Sequential zone-based: Partition nodes into spatial zones, activate sequentially",
        "zone_radius_latent_units": args.zone_radius,
        "activation_duration_seconds": args.activation_duration,
    }

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    with args.output_json.open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print("=" * 80)
    print("Cellulaire algorithm test completed")
    print("=" * 80)
    print(f"Input nodes                  : {result['metrics'].get('total_nodes', 0)}")
    print(f"Total zones created          : {result['metrics'].get('total_zones', 0)}")
    print(f"Avg nodes per zone           : {result['metrics'].get('avg_nodes_per_zone', 0):.2f}")
    print(f"Total activation events      : {result['metrics'].get('total_activation_events', 0)}")
    print(f"Total energy saved           : {result['metrics'].get('total_energy_saved_j', 0):.6f} J")
    print(f"Energy efficiency            : {result['metrics'].get('energy_efficiency_percent', 0):.2f}%")
    print(f"Total continuous energy      : {result['metrics'].get('total_continuous_energy_j', 0):.6f} J")
    print(f"Total cycle time             : {result['metrics'].get('total_cycle_time_seconds', 0):.2f} seconds")
    print(f"Coverage type                : {result['metrics'].get('coverage_type', 'N/A')}")
    print(f"Avg detection accuracy       : {result['metrics'].get('avg_detection_accuracy_percent', 0):.2f}%")
    print(f"Zone radius (latent units)   : {args.zone_radius}")
    print(f"Activation duration (s)      : {args.activation_duration}")
    print(f"Output JSON                  : {args.output_json.resolve()}")


if __name__ == "__main__":
    main()
