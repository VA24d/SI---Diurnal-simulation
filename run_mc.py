import os
import argparse
from pathlib import Path
import matplotlib.pyplot as plt

# Try to use the conda environment's python or standard setup
import geopandas as gpd

from src.diurnal_sim.io import load_buildings_and_boundary, validate_buildings_schema
from src.diurnal_sim.engine import DiurnalModelConfig
from src.diurnal_sim.mc import run_monte_carlo, MonteCarloConfig
from src.diurnal_sim.export import ExportPaths
import src.diurnal_sim.viz as viz

def main():
    parser = argparse.ArgumentParser(description="Run Diurnal Population Monte Carlo Simulation")
    parser.add_argument("--buildings", type=str, default="Buildings/WEST_ZONE_BLDG_HGT_POP_MEAN.shp", help="Path to buildings shapefile")
    parser.add_argument("--output", type=str, default="outputs", help="Output directory")
    parser.add_argument("--runs", type=int, default=10, help="Number of Monte Carlo runs (default 10 for quick testing)")
    args = parser.parse_args()

    buildings_path = Path(args.buildings)
    out_dir = Path(args.output)
    
    if not buildings_path.exists():
        print(f"Error: Buildings file {buildings_path} not found.")
        print("Please ensure you have the required shapefiles or update the path.")
        return

    print("Loading data...")
    # Since we are focusing on buildings, boundary is optional
    data = load_buildings_and_boundary(buildings_path=buildings_path)
    buildings = data.buildings
    
    print("Validating schema...")
    validate_buildings_schema(buildings, lulc_col="LU_B_PRJ", pop_col="B_POP_SHAR")

    # Set up Configs
    model_cfg = DiurnalModelConfig(
        day_of_week="Monday",
        time_interval_hours=0.5,
        lulc_col="LU_B_PRJ",
        pop_col="B_POP_SHAR",
        worker_share=0.40,
        minimal_presence_it=5,
        distance_decay_m=2000.0,
        assignment_by_type=True
    )
    
    mc_cfg = MonteCarloConfig(
        n_runs=args.runs,
        base_seed=42,
        percentiles=(5.0, 50.0, 95.0),
        key_hours=(6.0, 9.0, 12.0, 15.0, 18.0, 21.0)
    )

    print(f"Running Monte Carlo Simulation ({args.runs} runs)...")
    mc_summary = run_monte_carlo(
        buildings=buildings,
        model_config=model_cfg,
        mc_config=mc_cfg
    )

    print("Simulation complete. Generating outputs and visualizations...")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate static plots
    fig, ax = plt.subplots(figsize=(10, 6))
    viz.plot_uncertainty_band(
        mc_summary.timesteps,
        p5=mc_summary.total_population_percentiles[0],
        p50=mc_summary.total_population_percentiles[1],
        p95=mc_summary.total_population_percentiles[2],
        ax=ax,
        title=f"Monte Carlo Total Population (p5-p95, {args.runs} runs)"
    )
    fig.savefig(out_dir / "mc_total_population.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    
    # Save the time series mapping explicitly (since mc_summary doesn't have an export method like SimulationResult)
    import pandas as pd
    import numpy as np
    
    df_ts = pd.DataFrame({
        "time": mc_summary.timesteps,
        "p5": mc_summary.total_population_percentiles[0],
        "p50": mc_summary.total_population_percentiles[1],
        "p95": mc_summary.total_population_percentiles[2],
    })
    df_ts.to_csv(out_dir / "mc_timeseries.csv", index=False)
    
    np.save(out_dir / "mc_per_run_totals.npy", mc_summary.per_run_total)
    
    if mc_summary.building_percentiles_by_hour is not None:
        try:
            b_out = buildings.copy()
            # For each key hour, export the median (index 1 of percentiles)
            for i, h in enumerate(mc_summary.key_hours):
                b_out[f"pop_p50_{int(h):02d}h"] = mc_summary.building_percentiles_by_hour[i, 1, :]
            
            # Reproject for the GeoPackage if it doesn't have a valid CRS
            # Assuming epsg:4326 for web compatibility
            if b_out.crs and b_out.crs.to_epsg() != 4326:
                b_out = b_out.to_crs(epsg=4326)
            b_out.to_file(out_dir / "mc_buildings_snapshots.gpkg", driver="GPKG", layer="buildings_mc")
            
            # Simple snapshots maps
            for i, h in enumerate(mc_summary.key_hours):
                fig, ax = plt.subplots(figsize=(8, 8))
                viz.plot_map_snapshot(
                    b_out, 
                    values=b_out[f"pop_p50_{int(h):02d}h"].values,
                    ax=ax,
                    title=f"Est Population Map (Median) @ {int(h):02d}:00"
                )
                fig.savefig(out_dir / f"snapshot_{int(h):02d}h.png", dpi=150, bbox_inches="tight")
                plt.close(fig)
        except Exception as e:
            print(f"Warning: Failed to create geospatial snapshot files: {e}")

    print(f"Done! Check the '{out_dir}' folder for results.")

if __name__ == "__main__":
    main()
