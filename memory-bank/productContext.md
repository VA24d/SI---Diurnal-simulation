# Product Context

## Why this exists
Urban systems analysis often needs **time-of-day population** rather than static residential population. This project provides a simulation-based approach to estimate how many people are in each building across a day.

## What the user wants to do
- Load building footprints with attributes (land-use + estimated population).
- Run a day simulation and visualize:
  - Total population time series
  - Maps/snapshots at chosen hours
  - Animation playback
- Run Monte Carlo simulations to understand how uncertainty in assumptions changes results.

## Intended UX
Inside a notebook:
- A small control panel (widgets) to load data, set parameters, run single simulation / Monte Carlo, and export.
- Clear validation and status output.
- Visual outputs inline (plots and maps).
