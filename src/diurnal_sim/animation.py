from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np

from .engine import SimulationResult


@dataclass(frozen=True)
class AnimationPaths:
    mp4_path: Path


def save_map_animation(
    *,
    result: SimulationResult,
    mp4_path: str | Path,
    title: str = "Population map",
    cmap: str = "plasma",
    dpi: int = 150,
    fps: Optional[float] = None,
) -> AnimationPaths:
    """Save a simple building choropleth MP4 animation.

    Notes:
    - Requires `ffmpeg` available in PATH.
    - This is intentionally minimal (no basemap/roads). The notebook can optionally add those.
    """

    out = Path(mp4_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    buildings = result.buildings.copy()
    pop = result.population_matrix
    timesteps = result.timesteps

    vmin = float(np.nanmin(pop))
    vmax = float(np.nanmax(pop))

    if fps is None:
        # 24 seconds for a full day like the prototype.
        fps = max(1.0, len(timesteps) / 24.0)

    fig, ax = plt.subplots(1, 1, figsize=(10, 8))

    def _frame(i: int):
        ax.clear()
        buildings["value"] = pop[i, :]
        buildings.plot(
            column="value",
            cmap=cmap,
            ax=ax,
            vmin=vmin,
            vmax=vmax,
            legend=True,
            linewidth=0,
        )
        ax.set_title(f"{title} | t={timesteps[i]:.2f}h")
        ax.axis("off")
        return (ax,)

    anim = animation.FuncAnimation(fig, _frame, frames=len(timesteps), interval=1000 / fps, blit=False)
    writer = animation.FFMpegWriter(fps=fps, bitrate=3000)
    anim.save(out.as_posix(), writer=writer, dpi=dpi)
    plt.close(fig)

    return AnimationPaths(mp4_path=out)
