# Geospatial: Diurnal Population + Monte Carlo (Gachibowli)

This repository contains a clean Python implementation to simulate **diurnal population distribution** across buildings and run **Monte Carlo** scenarios to quantify uncertainty.

## Structure
- `src/diurnal_sim/`: reusable Python modules
- `notebooks/`: UI notebook (ipywidgets)
- `outputs/`: generated exports
- `memory-bank/`: project context docs

## Setup

Create/activate a Python environment, then:

```bash
python -m pip install -r requirements.txt
```

## Run
Open Jupyter and run the UI notebook:

```bash
jupyter notebook notebooks/DiurnalPopulation_MC_UI.ipynb
```

## Data
The default notebook expects local shapefiles similar to the original prototype:
- `Buildings/WEST_ZONE_BLDG_HGT_POP_MEAN.shp`
- `Boundary/UTM44N_GCKMMHS_ZONE_POLY_DSLV_EXTN.shp` (optional)

You can change paths from the notebook UI.
