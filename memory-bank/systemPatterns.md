# System Patterns

## Architecture (target)
Organize code into small modules:
- `io`: geospatial data loading + validation
- `model`: simulation configuration + schedules
- `engine`: diurnal simulation core
- `mc`: Monte Carlo runner + summarization (percentiles)
- `viz`: plotting maps/time series + animation helpers
- `export`: CSV/GeoPackage/MP4 writers

## Modeling pattern
### Single-run
- Inputs:
  - Buildings GeoDataFrame with land-use (e.g., `LU_B_PRJ`) and residential population (e.g., `B_POP_SHAR`).
  - Work schedules by destination building type.
- Outputs:
  - Population-by-building matrix over timesteps.
  - Aggregations by building type.

### Monte Carlo
Each run re-samples:
1) Work start/end times (within schedule distributions)
2) Workplace assignment (probabilistic assignment across candidate buildings)

Summaries computed across runs:
- time series percentiles (p5/p50/p95)
- optional per-building percentile snapshots at key hours

## UI pattern (notebook)
Widget-driven workflow:
1) Load/validate data
2) Configure parameters
3) Run (single / MC)
4) Visualize (time slider + charts)
5) Export
