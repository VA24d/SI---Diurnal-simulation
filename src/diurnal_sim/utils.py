from __future__ import annotations

import numpy as np


def sample_trunc_normal(
    rng: np.random.Generator,
    *,
    mean: float,
    std: float,
    min_val: float,
    max_val: float,
    size: int,
) -> np.ndarray:
    """Sample truncated normal via clip (fast, approximate)."""
    x = rng.normal(loc=mean, scale=std, size=size)
    return np.clip(x, min_val, max_val)


def format_time(hour: float) -> str:
    h = int(hour)
    m = int(round((hour - h) * 60))
    if m == 60:
        h += 1
        m = 0
    period = "AM" if h < 12 else "PM"
    h_12 = h if 1 <= h <= 12 else (h - 12 if h > 12 else 12)
    return f"{h_12:02d}:{m:02d} {period}"
