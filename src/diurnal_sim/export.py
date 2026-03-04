from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

import numpy as np
import pandas as pd
import geopandas as gpd

from .engine import SimulationResult


@dataclass(frozen=True)
class ExportPaths:
    output_dir: Path
    timeseries_csv: Path
    buildings_gpkg: Optional[Path]
    matrix_npy: Path
    metadata_json: Path


def export_simulation(
    *,
    result: SimulationResult,
    output_dir: str | Path,
    key_hours: Iterable[float] = (0.0, 6.0, 9.0, 12.0, 15.0, 18.0, 21.0, 23.0),
    gpkg_layer: str = "buildings",
) -> ExportPaths:
    """Export simulation outputs.

    Writes:
    - timeseries CSV
    - buildings GeoPackage with `pop_{hour}h` columns at key hours
    - population matrix .npy
    - metadata JSON
    """

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    # Time series
    ts = result.to_timeseries_df()
    timeseries_csv = out / "timeseries.csv"
    ts.to_csv(timeseries_csv, index=False)

    # Matrix
    matrix_npy = out / "population_matrix.npy"
    np.save(matrix_npy, result.population_matrix)

    # Metadata
    import json

    metadata_json = out / "metadata.json"
    with metadata_json.open("w") as f:
        json.dump(result.meta, f, indent=2)

    # Spatial snapshots
    buildings_gpkg: Optional[Path]
    try:
        buildings = result.buildings.copy()
        for h in key_hours:
            idx = int(round(float(h) / float(result.meta["time_interval_hours"])))
            idx = max(0, min(idx, result.population_matrix.shape[0] - 1))
            buildings[f"pop_{int(round(h)):02d}h"] = result.population_matrix[idx, :]

        buildings_gpkg = out / "buildings_snapshots.gpkg"
        buildings.to_file(buildings_gpkg, layer=gpkg_layer, driver="GPKG")
    except Exception:
        # Writing GeoPackage can fail if Fiona/GDAL isn't fully set up. Keep exports robust.
        buildings_gpkg = None

    return ExportPaths(
        output_dir=out,
        timeseries_csv=timeseries_csv,
        buildings_gpkg=buildings_gpkg,
        matrix_npy=matrix_npy,
        metadata_json=metadata_json,
    )
