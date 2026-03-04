# Progress

## Completed
- Read and analyzed existing notebook (`ADV.ipynb`) to understand current simulation approach and outputs.
- Confirmed scope and requirements with user (ipywidgets UI; MC over times + workplace assignment; local shapefiles; all outputs).
- Created Memory Bank structure and core documentation.

## In progress
- None yet (next phase is scaffolding + implementation).

## Next up
1) Create a clean project layout (`src/`, `notebooks/`, `outputs/`).
2) Implement data loading + validation.
3) Implement single-run simulation core.
4) Implement Monte Carlo runner + uncertainty summaries.
5) Build notebook UI and export pipeline.

## Known issues / risks
- Performance risk if we keep fully per-individual agent simulation for MC. We should prefer a more vectorized/aggregated approach to enable many runs.
