---
layout: default
title: Methodology
---

## System Architecture

The simulation is built on a modular Python architecture comprising:
- **`io`**: Geospatial data loading & validation
- **`model`**: Configuration and work schedules
- **`engine`**: The fast execution core assigning flows
- **`mc`**: Monte Carlo parallel runner
- **`viz`**: Data visualization mapping

## Simulation Mechanics

### 1. Distance Decay & Multinomial Assignment
Workers are assigned to destinations using a distance-decay gravity model. Each residential agent evaluates prospective workplaces using the following probability:
`P(work_j | res_i) ∝ exp(-Distance(i, j) / Decay_Constant)`

These probabilities form a distribution from which destinations are drawn via multinomial sampling.

### 2. Temporal Schedules
Work start and end times are sampled from truncated normal distributions specifically tailored to standard building types (e.g., IT vs. Non-IT Commercial vs. Recreation).

### 3. Monte Carlo Executions
Uncertainty is intrinsic to gravity models. By running $N$ Monte Carlo iterations, we compute the structural uncertainty embedded within our spatial assignment logic and scheduling variations. 

[⬅ Back to Home](./index.html){: .btn }
