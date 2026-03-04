from __future__ import annotations

from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
import geopandas as gpd


def plot_total_timeseries(
    timesteps: np.ndarray,
    total: np.ndarray,
    *,
    ax: Optional[plt.Axes] = None,
    title: str = "Total population over time",
) -> plt.Axes:
    ax = ax or plt.gca()
    ax.plot(timesteps, total, linewidth=2.5)
    ax.set_xlabel("Hour of day")
    ax.set_ylabel("Population")
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 24)
    return ax


def plot_uncertainty_band(
    timesteps: np.ndarray,
    p5: np.ndarray,
    p50: np.ndarray,
    p95: np.ndarray,
    *,
    ax: Optional[plt.Axes] = None,
    title: str = "Monte Carlo total population (p5–p95)",
) -> plt.Axes:
    ax = ax or plt.gca()
    ax.fill_between(timesteps, p5, p95, alpha=0.25, label="p5–p95")
    ax.plot(timesteps, p50, linewidth=2.5, label="median")
    ax.set_xlabel("Hour of day")
    ax.set_ylabel("Population")
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 24)
    ax.legend()
    return ax


def plot_map_snapshot(
    buildings: gpd.GeoDataFrame,
    values: np.ndarray,
    *,
    ax: Optional[plt.Axes] = None,
    cmap: str = "YlOrRd",
    vmin: Optional[float] = None,
    vmax: Optional[float] = None,
    title: str = "Population snapshot",
) -> plt.Axes:
    ax = ax or plt.gca()
    gdf = buildings.copy()
    gdf["value"] = values
    gdf.plot(column="value", cmap=cmap, ax=ax, vmin=vmin, vmax=vmax, legend=True, linewidth=0)
    ax.set_title(title)
    ax.axis("off")
    return ax
