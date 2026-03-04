# Project Brief: Gachibowli Diurnal Population Simulation

## Goal
Build a clean, reproducible Python implementation (with an **ipywidgets-based notebook UI**) that simulates **diurnal population distribution** across buildings in Gachibowli, Hyderabad, using building land-use classes and employment/work schedules.

The new implementation must also support **Monte Carlo simulations** to quantify uncertainty (specifically over **work start/end times** and **workplace assignment**).

## Primary Deliverables
1. A modular Python implementation (importable modules) suitable for reuse.
2. A Jupyter notebook (`.ipynb`) acting as the main UI using ipywidgets.
3. Export pipelines for:
   - Time series CSV
   - Spatial snapshots (GeoPackage preferred)
   - MP4 animations (optional, for selected scenario)
4. Documentation to run and reproduce results.

## Success Criteria
- Runs end-to-end using existing local shapefiles (Buildings + optional Boundary).
- UI provides parameter controls and run buttons.
- Monte Carlo runs generate uncertainty bands (p5–p95) and spatial uncertainty metrics.
- Outputs saved under `outputs/`.

## Constraints
- Implementation must be clean “from scratch” (not incremental edits inside the current notebook).
- Prefer reproducibility (explicit random seeds, deterministic exports).
- Keep code minimal but correct; avoid overly slow per-agent loops where possible.
