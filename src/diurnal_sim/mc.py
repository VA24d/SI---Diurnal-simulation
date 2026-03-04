from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

import numpy as np

import geopandas as gpd

from .engine import DiurnalModel, DiurnalModelConfig, SimulationResult


@dataclass(frozen=True)
class MonteCarloConfig:
    n_runs: int = 50
    base_seed: int = 0
    percentiles: tuple[float, float, float] = (5.0, 50.0, 95.0)
    key_hours: tuple[float, ...] = (6.0, 9.0, 12.0, 15.0, 18.0, 21.0)


@dataclass(frozen=True)
class MonteCarloSummary:
    timesteps: np.ndarray
    # (P, T)
    total_population_percentiles: np.ndarray
    # (H, P, B) percentiles at key hours for building-level maps
    building_percentiles_by_hour: Optional[np.ndarray]
    key_hours: tuple[float, ...]
    # Optional: store per-run results (can be large)
    per_run_total: Optional[np.ndarray]
    meta: Dict[str, object]


def run_monte_carlo(
    *,
    buildings: gpd.GeoDataFrame,
    model_config: Optional[DiurnalModelConfig] = None,
    mc_config: Optional[MonteCarloConfig] = None,
) -> MonteCarloSummary:
    mc_cfg = mc_config or MonteCarloConfig()
    model_cfg = model_config or DiurnalModelConfig()

    if mc_cfg.n_runs <= 0:
        raise ValueError("n_runs must be > 0")

    totals = []
    snapshots_by_hour = {h: [] for h in mc_cfg.key_hours}
    timesteps: Optional[np.ndarray] = None

    for i in range(mc_cfg.n_runs):
        seed = int(mc_cfg.base_seed) + i
        model = DiurnalModel(buildings, config=model_cfg)
        result: SimulationResult = model.run(seed=seed)
        if timesteps is None:
            timesteps = result.timesteps
        totals.append(result.total_population_series())

        # Store per-building snapshots at key hours
        for h in mc_cfg.key_hours:
            idx = int(round(float(h) / float(result.meta["time_interval_hours"])))
            idx = max(0, min(idx, result.population_matrix.shape[0] - 1))
            snapshots_by_hour[h].append(result.population_matrix[idx, :].astype(np.float32))

    per_run_total = np.stack(totals, axis=0)  # (R, T)
    pct = np.percentile(per_run_total, q=list(mc_cfg.percentiles), axis=0)

    # Building-level percentiles per key hour: (H, P, B)
    building_percentiles_by_hour: Optional[np.ndarray]
    if len(mc_cfg.key_hours) > 0:
        hour_arrays = []
        for h in mc_cfg.key_hours:
            runs_x_b = np.stack(snapshots_by_hour[h], axis=0)  # (R, B)
            hour_arrays.append(np.percentile(runs_x_b, q=list(mc_cfg.percentiles), axis=0).astype(np.float32))
        building_percentiles_by_hour = np.stack(hour_arrays, axis=0)
    else:
        building_percentiles_by_hour = None

    meta: Dict[str, object] = {
        "n_runs": mc_cfg.n_runs,
        "base_seed": mc_cfg.base_seed,
        "percentiles": mc_cfg.percentiles,
        "key_hours": mc_cfg.key_hours,
        **result.meta,
    }

    return MonteCarloSummary(
        timesteps=timesteps if timesteps is not None else np.array([]),
        total_population_percentiles=pct,
        building_percentiles_by_hour=building_percentiles_by_hour,
        key_hours=mc_cfg.key_hours,
        per_run_total=per_run_total,
        meta=meta,
    )