from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import geopandas as gpd


@dataclass(frozen=True)
class LoadedData:
    buildings: gpd.GeoDataFrame
    boundary: Optional[gpd.GeoDataFrame]


def load_buildings_and_boundary(
    *,
    buildings_path: str | Path,
    boundary_path: str | Path | None = None,
) -> LoadedData:
    """Load buildings and (optionally) boundary.

    Raises:
        FileNotFoundError: if buildings_path does not exist.
    """

    bpath = Path(buildings_path)
    if not bpath.exists():
        raise FileNotFoundError(f"Buildings file not found: {bpath}")

    buildings = gpd.read_file(bpath)

    boundary: Optional[gpd.GeoDataFrame] = None
    if boundary_path is not None:
        p = Path(boundary_path)
        if p.exists():
            boundary = gpd.read_file(p)
        else:
            boundary = None

    return LoadedData(buildings=buildings, boundary=boundary)


def validate_buildings_schema(
    buildings: gpd.GeoDataFrame,
    *,
    lulc_col: str,
    pop_col: str,
) -> None:
    missing = [c for c in [lulc_col, pop_col] if c not in buildings.columns]
    if missing:
        raise ValueError(
            "Buildings GeoDataFrame missing required columns: "
            + ", ".join(missing)
            + f". Available columns: {list(buildings.columns)}"
        )
