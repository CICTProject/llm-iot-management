import json
from pathlib import Path
from typing import Dict, Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import FuncFormatter


# Data loading and processing
def load_results(results_dir: Path = Path("results/algorithms")) -> Dict[str, Dict[str, Any]]:
    """Load algorithm result JSON files."""
    results = {}

    for algo_file in ["naive_result.json", "cellulaire_result.json", "probabilistic_result.json"]:
        file_path = results_dir / algo_file
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                results[algo_file.replace("_result.json", "")] = json.load(f)

    return results


def extract_metrics(results: Dict[str, Dict[str, Any]]) -> pd.DataFrame:
    """Extract key metrics from all algorithms into a unified DataFrame."""
    data = []

    for algo_name, result in results.items():
        metrics = result.get("metrics", {})

        # Active nodes
        if algo_name == "naive":
            active_nodes = metrics.get("activated_nodes", 0)
        elif algo_name == "cellulaire":
            active_nodes = metrics.get("total_zones", 0) * metrics.get("avg_nodes_per_zone", 0)
        elif algo_name == "probabilistic":
            active_nodes = metrics.get("selected_nodes", 0)
        else:
            active_nodes = 0

        # Energy in Joules
        if algo_name == "naive":
            energy_j = metrics.get("total_energy_consumed_j", 0)
            # Convert string efficiency to numeric
            eff_str = metrics.get("energy_efficiency", "low")
            efficiency = 100.0 if isinstance(eff_str, str) else float(eff_str)
        elif algo_name == "cellulaire":
            energy_j = metrics.get("total_nodes_energy_j", 0) - metrics.get("total_energy_saved_j", 0)
            efficiency = metrics.get("energy_efficiency_percent", 0)
        elif algo_name == "probabilistic":
            # Original metric is in Wh -> convert to J
            energy_j = metrics.get("total_activation_energy_wh", 0) * 3600
            efficiency = metrics.get("coverage_selection_efficiency", 0)
        else:
            energy_j = 0
            efficiency = 0.0

        data.append({
            "Algorithm": algo_name.capitalize(),
            "Active Nodes": active_nodes,
            "Total Nodes": metrics.get("total_nodes", 10000),
            "Energy (J)": energy_j,
            "Efficiency (%)": efficiency,
        })

    df = pd.DataFrame(data)

    # Optional fixed ordering
    order = ["Naive", "Cellulaire", "Probabilistic"]
    df["Algorithm"] = pd.Categorical(df["Algorithm"], categories=order, ordered=True)
    df = df.sort_values("Algorithm").reset_index(drop=True)
    # Convert categorical back to string for matplotlib compatibility
    df["Algorithm"] = df["Algorithm"].astype(str)

    return df


# Styling utilities
def set_style() -> None:
    """Set a clean style."""
    plt.rcParams.update({
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
        "axes.edgecolor": "#333333",
        "axes.linewidth": 1.0,
        "axes.grid": False,
        "grid.color": "#D9D9D9",
        "grid.linestyle": "--",
        "grid.linewidth": 0.7,
        "grid.alpha": 0.6,
        "font.family": "serif",
        "font.size": 11,
        "axes.titlesize": 16,
        "axes.titleweight": "bold",
        "axes.labelsize": 13,
        "axes.labelweight": "bold",
        "xtick.labelsize": 11,
        "ytick.labelsize": 11,
        "legend.fontsize": 11,
    })


def thousands_formatter(x, _):
    return f"{int(x):,}"


def add_bar_labels(ax, bars, fmt="{:.2f}", suffix="", inside=False, color="#222222") -> None:
    """Add value labels above or inside bars."""
    y_min, y_max = ax.get_ylim()
    offset = (y_max - y_min) * 0.015

    for bar in bars:
        height = bar.get_height()
        x = bar.get_x() + bar.get_width() / 2

        if inside and height > 0:
            ax.text(
                x, height / 2,
                f"{fmt.format(height)}{suffix}",
                ha="center", va="center",
                fontsize=11, fontweight="bold", color="white"
            )
        else:
            ax.text(
                x, height + offset,
                f"{fmt.format(height)}{suffix}",
                ha="center", va="bottom",
                fontsize=11, fontweight="bold", color=color
            )


def style_axis(ax) -> None:
    """Apply common axis styling."""
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#444444")
    ax.spines["bottom"].set_color("#444444")
    ax.tick_params(axis="both", colors="#333333")
    ax.grid(axis="y", linestyle="--", alpha=0.45)
    ax.set_axisbelow(True)


# Visualization functions
def create_visualizations(
    results: Dict[str, Dict[str, Any]],
    output_dir: Path = Path("results/benchmark/figures")
) -> pd.DataFrame:
    """Create comparison charts."""
    output_dir.mkdir(parents=True, exist_ok=True)

    set_style()
    df = extract_metrics(results)

    # Refined color palette
    colors = ["#4C78A8", "#72B7B2", "#B279A2"]

    # Chart 1: Energy Consumption
    fig, ax = plt.subplots(figsize=(9, 6))
    bars = ax.bar(
        df["Algorithm"], df["Energy (J)"],
        color=colors, edgecolor="#2F2F2F", linewidth=1.1, width=0.65
    )
    ax.set_title("Total Energy Consumption Comparison", pad=12)
    ax.set_ylabel("Energy (J)")
    ax.yaxis.set_major_formatter(FuncFormatter(thousands_formatter))
    style_axis(ax)
    add_bar_labels(ax, bars, fmt="{:,.2f}")
    fig.tight_layout()
    fig.savefig(output_dir / "energy_consumption.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    # Chart 2: Energy Efficiency
    fig, ax = plt.subplots(figsize=(9, 6))
    bars = ax.bar(
        df["Algorithm"], df["Efficiency (%)"],
        color=colors, edgecolor="#2F2F2F", linewidth=1.1, width=0.65
    )
    ax.set_title("Energy Efficiency Comparison", pad=12)
    ax.set_ylabel("Efficiency (%)")
    ax.set_ylim(0, max(100, df["Efficiency (%)"].max() * 1.15))
    style_axis(ax)
    add_bar_labels(ax, bars, fmt="{:.2f}", suffix="%")
    fig.tight_layout()
    fig.savefig(output_dir / "energy_efficiency.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    # Chart 3: Active Nodes
    fig, ax = plt.subplots(figsize=(10, 6.5))
    bars = ax.bar(
        df["Algorithm"], df["Active Nodes"],
        color=colors, edgecolor="#2F2F2F", linewidth=1.1, width=0.65
    )

    total_nodes = int(df["Total Nodes"].max())

    ax.axhline(
        y=total_nodes,
        color="#B22222",
        linestyle="--",
        linewidth=1.5,
        alpha=0.8,
        label=f"Total Nodes = {total_nodes:,}"
    )

    ax.set_title("Active Nodes Comparison", pad=12)
    ax.set_ylabel("Number of Nodes")
    ax.yaxis.set_major_formatter(FuncFormatter(thousands_formatter))
    ax.set_ylim(0, total_nodes * 1.12)
    style_axis(ax)
    add_bar_labels(ax, bars, fmt="{:,.0f}")
    ax.legend(frameon=False, loc="upper right")
    fig.tight_layout()
    fig.savefig(output_dir / "active_nodes.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    return df


# Main execution
def main() -> None:
    print("\nLoading algorithm results...")
    results = load_results()

    if not results:
        print("No result files found in results/algorithms/")
        return

    print(f"Loaded {len(results)} algorithm result files.")

    print("\nExtracting metrics...")
    df = extract_metrics(results)
    print(df)

    print("\nCreating visualizations...")
    create_visualizations(results)

    print("\nAll charts have been saved successfully.")


if __name__ == "__main__":
    main()