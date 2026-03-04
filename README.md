<div align="center">
  <img src="docs/assets/img/logo.png" alt="Diurnal Population Simulation Logo" width="200"/>
  <h1>Diurnal Population Simulation & Monte Carlo Engine</h1>
  <p><em>A Python-based geospatial toolkit for modeling and simulating day-to-night urban population shifts with Monte Carlo uncertainty analysis.</em></p>
  <p>
    <a href="https://github.com/va/Geospatial/actions"><img src="https://img.shields.io/badge/build-passing-brightgreen" alt="Build Status"></a>
    <a href="https://python.org"><img src="https://img.shields.io/badge/python-3.12-blue.svg" alt="Python Version"></a>
    <a href="https://geopandas.org"><img src="https://img.shields.io/badge/geopandas-supported-green" alt="Geopandas"></a>
  </p>
</div>

---

## 📌 Overview

Traditional census data often provides a static "nighttime-only" view of population distribution based on residential locations. However, during the day, populations shift dramatically towards commercial hubs, schools, and offices. 

This repository provides a robust Python engine to:
1. **Simulate Diurnal Shifts:** Distribute populations dynamically across buildings using heuristic-based transition models between Daytime and Nighttime.
2. **Quantify Uncertainty (Monte Carlo):** Run hundreds of iterations of the simulation by perturbing key parameters (e.g., student and worker percentages) to understand the confidence intervals of the resulting population distributions.
3. **Visualize the Results:** Automatically generate 3D choropleth maps, static bounds maps, and animated day-night transitions using Plotly and Folium.

## 🚀 Quick Start

### 1. Requirements

Ensure you have Anaconda installed and use the default `python` command pointing to your active environment. 

```bash
# Clone the repository
git clone https://github.com/va/Geospatial.git
cd Geospatial

# Install dependencies
python -m pip install -r requirements.txt
```

### 2. Running the Interactive UI

The easiest way to explore the project is via the interactive Jupyter Notebook widget UI.

```bash
jupyter notebook notebooks/DiurnalPopulation_MC_UI.ipynb
```

From here, you can load shapefiles, tune global population configurations, run simulations, and directly export maps to HTML.

### 3. Simulation Demo

<div align="center">
  <video width="80%" controls style="border-radius: 8px; margin-top: 15px;">
    <source src="docs/assets/img/demo.mp4" type="video/mp4">
    Your browser does not support the video tag.
  </video>
  <p><em>Example simulation showcasing dynamic population shifts over 24 hours.</em></p>
</div>

### 4. Running Headless (CLI)

You can also run a pre-configured Monte Carlo simulation directly from the terminal without the UI:

```bash
python run_mc.py
```

## 📂 Repository Structure

```text
Geospatial/
├── docs/               # GitHub Pages website & documentation
├── memory-bank/        # Architectural and contextual documentation
├── notebooks/          # Exploratory notebooks & UI interfaces (e.g., DiurnalPopulation_MC_UI.ipynb)
├── outputs/            # Generated outputs (HTML maps, animated Plotly figures, CSV summaries)
├── src/
│   └── diurnal_sim/    # Core reusable Python package
│       ├── config.py     # Configuration and default bounds
│       ├── engine.py     # Deterministic simulation logic
│       ├── mc.py         # Monte Carlo wrapper for uncertainty
│       ├── viz.py        # 3D and 2D mapping tools
│       ├── animation.py  # Plotly animated map generation
│       ├── import.py     # Shapefile parsing and cleaning
│       └── export.py     # Data exporting utilities
├── run_mc.py           # Example driver script for headless execution
└── requirements.txt    # Project dependencies
```

## 🛠️ Core Technology Stack

- **Geospatial Processing:** `geopandas`, `shapely`
- **Simulation & Math:** `pandas`, `numpy`, `scipy`
- **Visualization:** `plotly`, `folium`
- **Interactivity:** `ipywidgets`

## 🧠 Methodology

For an in-depth breakdown of the algorithmic approach, data preprocessing pipelines, heuristics used for population assignment, and Monte Carlo permutation logic, please observe the [Methodology Documentation](docs/methodology.md) and our [Memory Bank contextual files](memory-bank/).
