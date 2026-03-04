from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

import numpy as np
import pandas as pd
import geopandas as gpd

from .config import LulcCodes, WorkSchedules, is_working_day
from .utils import sample_trunc_normal


@dataclass(frozen=True)
class DiurnalModelConfig:
    day_of_week: str = "Monday"
    time_interval_hours: float = 0.5
    lulc_col: str = "LU_B_PRJ"
    pop_col: str = "B_POP_SHAR"
    # Fraction of residential population treated as workers.
    # In the original notebook this emerges from the employment distribution; here we keep it explicit.
    worker_share: float = 0.40
    # For IT buildings: constant minimal presence.
    minimal_presence_it: int = 5
    # Workplace assignment: distance decay (meters). Larger => more diffuse assignment.
    distance_decay_m: float = 2000.0
    # If True, normalize assignment within each destination type.
    assignment_by_type: bool = True
    # Split of worker destinations across schedule types (must sum to 1.0). If None, equal split.
    dest_type_shares: Optional[Dict[str, float]] = None


@dataclass(frozen=True)
class SimulationResult:
    timesteps: np.ndarray  # (T,)
    population_matrix: np.ndarray  # (T, B)
    buildings: gpd.GeoDataFrame
    meta: Dict[str, object]

    def total_population_series(self) -> np.ndarray:
        return self.population_matrix.sum(axis=1)

    def to_timeseries_df(self) -> pd.DataFrame:
        total = self.total_population_series()
        return pd.DataFrame({"time": self.timesteps, "total_population": total})


class DiurnalModel:
    """Monte-Carlo-friendly diurnal model.

    This is intentionally more aggregated than a full per-individual agent model.
    """

    def __init__(self, buildings: gpd.GeoDataFrame, config: Optional[DiurnalModelConfig] = None):
        self.buildings = buildings.copy()
        self.config = config or DiurnalModelConfig()

        self._prepare_columns()

    def _prepare_columns(self) -> None:
        cfg = self.config
        if cfg.lulc_col not in self.buildings.columns:
            raise ValueError(f"Missing land-use column '{cfg.lulc_col}'")
        if cfg.pop_col not in self.buildings.columns:
            raise ValueError(f"Missing population column '{cfg.pop_col}'")

        self.buildings["building_type"] = self.buildings[cfg.lulc_col].map(LulcCodes)
        self.buildings["residential_pop"] = (
            pd.to_numeric(self.buildings[cfg.pop_col], errors="coerce").fillna(0).clip(lower=0).astype(int)
        )

        # Minimal presence in Commercial-IT
        self.buildings["minimal_presence"] = 0
        it_mask = self.buildings["building_type"] == "Commercial-IT"
        self.buildings.loc[it_mask, "minimal_presence"] = int(cfg.minimal_presence_it)

        # Cache centroids for distance computations.
        self.buildings["centroid"] = self.buildings.geometry.centroid

    def _compute_distance_matrix_m(
        self, origin_idx: np.ndarray, dest_idx: np.ndarray
    ) -> np.ndarray:
        """Compute pairwise distances between origin and destination centroids.

        Assumes projected CRS in meters. If CRS is geographic, this will be wrong; callers should
        reproject before running.
        """
        o = self.buildings.loc[origin_idx, "centroid"].values
        d = self.buildings.loc[dest_idx, "centroid"].values
        # Shapely distance operates elementwise; use nested loops is slow. Instead we pull x/y.
        ox = np.array([p.x for p in o])
        oy = np.array([p.y for p in o])
        dx = np.array([p.x for p in d])
        dy = np.array([p.y for p in d])
        # (O,1) - (1,D) broadcast
        return np.sqrt((ox[:, None] - dx[None, :]) ** 2 + (oy[:, None] - dy[None, :]) ** 2)

    def _assign_workplace_flows(
        self,
        rng: np.random.Generator,
        *,
        residential_idx: np.ndarray,
        worker_counts: np.ndarray,
        dest_idx_by_type: Dict[str, np.ndarray],
        dest_type_shares: Dict[str, float],
    ) -> np.ndarray:
        """Assign residential workers to destination buildings via multinomial draws.

        Returns:
            flows_to_dest: (B,) array with number of workers assigned to each building.
        """
        cfg = self.config
        B = len(self.buildings)
        flows_to_dest = np.zeros(B, dtype=np.int64)

        # Precompute per-type distance->probability matrices once.
        probs_by_type: Dict[str, np.ndarray] = {}
        active_types: list[str] = []
        active_shares: list[float] = []

        for schedule_code, dest_idx in dest_idx_by_type.items():
            if dest_idx.size == 0:
                continue
            if not is_working_day(cfg.day_of_week, schedule_code):
                continue

            share = float(dest_type_shares.get(schedule_code, 0.0))
            if share <= 0.0:
                continue

            dist_m = self._compute_distance_matrix_m(residential_idx, dest_idx)
            weights = np.exp(-dist_m / max(1.0, cfg.distance_decay_m))
            row_sums = weights.sum(axis=1, keepdims=True)
            probs = np.divide(weights, row_sums, out=np.zeros_like(weights), where=row_sums > 0)

            probs_by_type[schedule_code] = probs
            active_types.append(schedule_code)
            active_shares.append(share)

        if not active_types:
            return flows_to_dest

        # Normalize shares over active types.
        share_arr = np.array(active_shares, dtype=np.float64)
        share_arr = share_arr / share_arr.sum()

        # For each residential building, split workers across schedule types ONCE (multinomial)
        # then assign to destination buildings for each type (multinomial).
        for r_i, n_workers in enumerate(worker_counts):
            if n_workers <= 0:
                continue
            n_workers_by_type = rng.multinomial(int(n_workers), share_arr)
            for j, schedule_code in enumerate(active_types):
                n_for_type = int(n_workers_by_type[j])
                if n_for_type <= 0:
                    continue
                dest_idx = dest_idx_by_type[schedule_code]
                draw = rng.multinomial(n_for_type, probs_by_type[schedule_code][r_i])
                flows_to_dest[dest_idx] += draw.astype(np.int64)

        return flows_to_dest

    def run(self, *, seed: int = 0) -> SimulationResult:
        cfg = self.config
        rng = np.random.default_rng(seed)

        timesteps = np.arange(0.0, 24.0 + cfg.time_interval_hours, cfg.time_interval_hours)
        T = len(timesteps)
        B = len(self.buildings)

        # Residential origins
        residential_mask = self.buildings["building_type"] == "Residential"
        residential_idx = self.buildings.index[residential_mask].to_numpy()
        residential_pop = self.buildings.loc[residential_idx, "residential_pop"].to_numpy(dtype=np.int64)

        # Total workers per residential building
        worker_counts = np.floor(residential_pop * float(cfg.worker_share)).astype(np.int64)
        nonworker_counts = residential_pop - worker_counts

        # Destination candidates by schedule type.
        dest_idx_by_type: Dict[str, np.ndarray] = {}
        for schedule_code in WorkSchedules.keys():
            dest_type_name = LulcCodes.get(schedule_code)
            if dest_type_name is None:
                dest_idx_by_type[schedule_code] = np.array([], dtype=int)
                continue
            dest_mask = self.buildings["building_type"] == dest_type_name
            dest_idx_by_type[schedule_code] = self.buildings.index[dest_mask].to_numpy()

        # Destination type shares
        if cfg.dest_type_shares is None:
            working_types = [
                code
                for code in WorkSchedules.keys()
                if is_working_day(cfg.day_of_week, code) and dest_idx_by_type.get(code, np.array([])).size > 0
            ]
            if len(working_types) == 0:
                dest_type_shares: Dict[str, float] = {code: 0.0 for code in WorkSchedules.keys()}
            else:
                eq = 1.0 / float(len(working_types))
                dest_type_shares = {code: (eq if code in working_types else 0.0) for code in WorkSchedules.keys()}
        else:
            # Normalize user-provided mapping.
            total_share = float(sum(max(0.0, v) for v in cfg.dest_type_shares.values()))
            if total_share <= 0:
                raise ValueError("dest_type_shares must sum to > 0")
            dest_type_shares = {
                code: float(max(0.0, cfg.dest_type_shares.get(code, 0.0))) / total_share
                for code in WorkSchedules.keys()
            }

        # Assign workers to destination buildings (counts per building)
        workers_at_dest = self._assign_workplace_flows(
            rng,
            residential_idx=residential_idx,
            worker_counts=worker_counts,
            dest_idx_by_type=dest_idx_by_type,
            dest_type_shares=dest_type_shares,
        )

        # Sample schedule times per schedule_code to create time-at-work factor per timestep.
        # We treat a schedule as: for that destination type, workers are present if t in [start,end].
        # For Monte Carlo, we resample these times each run.
        workers_present_factor_by_code: Dict[str, np.ndarray] = {}
        for schedule_code, sched in WorkSchedules.items():
            if not is_working_day(cfg.day_of_week, schedule_code):
                workers_present_factor_by_code[schedule_code] = np.zeros(T, dtype=float)
                continue
            start = float(
                sample_trunc_normal(
                    rng,
                    mean=sched.start_mean,
                    std=sched.start_std,
                    min_val=sched.start_min,
                    max_val=sched.start_max,
                    size=1,
                )[0]
            )
            end = float(
                sample_trunc_normal(
                    rng,
                    mean=sched.end_mean,
                    std=sched.end_std,
                    min_val=sched.end_min,
                    max_val=sched.end_max,
                    size=1,
                )[0]
            )
            if end < start:
                # Extremely unlikely given params, but guard anyway.
                start, end = min(start, end), max(start, end)
            workers_present_factor_by_code[schedule_code] = ((timesteps >= start) & (timesteps <= end)).astype(float)

        # Build base population matrix: start with all residential population at home.
        pop = np.zeros((T, B), dtype=np.float32)
        for t_i in range(T):
            pop[t_i, residential_idx] += (worker_counts + nonworker_counts).astype(np.float32)

        # Move workers from home to destinations at active times.
        # We apply per-type schedule factors to the destination buildings, then subtract
        # the corresponding number of active workers from homes (conserving total pop).
        total_workers_assigned = int(workers_at_dest.sum())
        if total_workers_assigned > 0:
            active_workers_total_by_t = np.zeros(T, dtype=np.float32)

            for schedule_code, dest_idx in dest_idx_by_type.items():
                if dest_idx.size == 0:
                    continue
                factor = workers_present_factor_by_code.get(schedule_code)
                if factor is None:
                    continue

                dest_workers = workers_at_dest[dest_idx].astype(np.float32)
                dest_workers_sum = float(dest_workers.sum())
                if dest_workers_sum <= 0:
                    continue

                for t_i in range(T):
                    if factor[t_i] <= 0:
                        continue
                    pop[t_i, dest_idx] += dest_workers
                    active_workers_total_by_t[t_i] += dest_workers_sum

            # Subtract active workers from homes proportionally to each residential building's worker count.
            total_home_workers = float(worker_counts.sum())
            if total_home_workers > 0:
                home_worker_weights = worker_counts.astype(np.float32) / total_home_workers
                for t_i in range(T):
                    if active_workers_total_by_t[t_i] <= 0:
                        continue
                    pop[t_i, residential_idx] -= active_workers_total_by_t[t_i] * home_worker_weights

        # Minimal presence
        pop += self.buildings["minimal_presence"].to_numpy(dtype=np.float32)[None, :]
        pop = np.clip(pop, 0, None)

        meta: Dict[str, object] = {
            "day_of_week": cfg.day_of_week,
            "time_interval_hours": cfg.time_interval_hours,
            "seed": seed,
            "worker_share": cfg.worker_share,
            "distance_decay_m": cfg.distance_decay_m,
            "dest_type_shares": dest_type_shares,
        }

        return SimulationResult(timesteps=timesteps, population_matrix=pop, buildings=self.buildings, meta=meta)