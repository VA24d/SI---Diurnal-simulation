# Active Context

## Current focus
Rebuild the diurnal population simulator as a clean, modular implementation and add Monte Carlo support.

## What we learned from the existing notebook
`ADV.ipynb` already implements:
- Building classification using `LU_B_PRJ`
- Residential population from `B_POP_SHAR`
- Worker/non-worker split via employment distribution
- Workplace assignment (nearest building by type)
- Time stepping over 24h (default 30-minute intervals)
- Map snapshots + MP4 animation exports

## Decisions (confirmed with user)
- UI will be inside notebook via **ipywidgets**.
- Monte Carlo uncertainties will include:
  - Work start/end times
  - Workplace assignment
- Shapefiles are available locally (no synthetic demo mode required).
- UI should support all outputs: snapshots, playback, uncertainty bands, exports.

## Next steps
1) Scaffold project structure and dependencies.
2) Implement fast simulation core suitable for Monte Carlo.
3) Build the ipywidgets notebook UI.
