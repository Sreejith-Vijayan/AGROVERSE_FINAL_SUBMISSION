# AGROVERSE — Integrated Farm Resilience & Agro-Climatic Intelligence Platform

[![NASA Space Apps Challenge 2026](https://img.shields.io/badge/NASA%20Space%20Apps-2026-blue.svg)](https://www.spaceappschallenge.org/)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Flask 3.0+](https://img.shields.io/badge/Flask-3.0+-000000.svg?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Test Suite: Passing](https://img.shields.io/badge/pytest-passing-brightgreen.svg)](tests/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **NASA Space Apps Challenge 2026**  
> **Challenge Track:** *"Field Shift: Adapting Farms with NASA Data"*  
> **Target Location:** Palakkad Demo Farm, Chittur-Kollengode Agricultural Corridor, Kerala, India (`10.708° N, 76.639° E`)

---

## 1. Executive Summary & Integration Architecture

**AGROVERSE** has been unified into a single, comprehensive agricultural intelligence platform combining:
1. **Core AGROVERSE Platform:** Empirical NASA POWER and SMAP satellite data pipelines, interactive dashboard, date range explorer, inline SVG trend charts, and Leaflet GIS mapping.
2. **Member 3 Final Climate & Risk Handover:** Daily and monthly historical time series, extreme rainfall logs (`top_rainfall_days.csv`), dry spell catalogs (`dry_periods.csv`), and integrated climate-risk assessments (`risk_assessment.csv`).
3. **Member 4 Agriculture Knowledge Base:** Sourced requirements from Kerala Agricultural University (KAU PoP 2016), ICAR-CPCRI, ICAR-CTCRI, and IMD covering the 6 mandated crops (Rice, Groundnut, Banana, Coconut, Tapioca, Sugarcane).
4. **Decision Support Engine:** Transparent, explainable crop suitability screening answering *"What Should I Grow Now?"*.
5. **What-If Climate Scenario Simulator:** Interactive sensitivity engine answering *"What happens to crop suitability if rainfall decreases, temperature increases, or dry spells lengthen?"*.

---

## 2. Spatial Locations & Source Registry Integrity

### Spatial Distinction Notice
To preserve scientific integrity, differing spatial observation points are explicitly distinguished and not conflated:
- **Palakkad Demo Farm (`10.708° N, 76.639° E`):** Primary verified field site in the Chittur-Kollengode corridor used for NASA POWER agro-climatology and SMAP satellite cell extractions.
- **Palakkad Town / District Reference (`10.7867° N, 76.6548° E`):** Regional meteorological reference point located ~11 km to the northeast. Handover records tied to this location are retained with spatial attribution rather than assumed to be on-farm readings.

### Source Registry Table
| Dataset | Source | Time Period | Native Resolution | Verification Status | Intended Use |
|---|---|---|---|---|---|
| NASA POWER Climatology | NASA Langley Research Center | 2020–2025 | 0.5° × 0.625° | Verified Empirical | Baseline rainfall, temperature, heat index |
| NASA SMAP L3 Soil Moisture (Monthly) | NASA SMAP Mission (via Member 3) | 2020–2025 | ~36 km Grid | Empirical Handover | Monthly regional surface soil moisture dynamics |
| SMAP Daily Proxy (`smap_daily_cleaned.csv`) | Derived from NASA POWER GWETROOT | 2020–2025 | Point Proxy | Simulated / Demo Proxy | Demonstration of daily soil moisture series (`SIMULATED_DAILY_PROXY`; not actual daily SMAP satellite observations) |
| Member 3 Handover Data | Member 3 Analysis | 2020–2025 | Monthly / Daily Logs | Verified Handover | Integrated risk assessment, extreme event catalogs |
| Palakkad Agriculture KB | KAU, ICAR-CPCRI, CTCRI, TNAU | Agronomic Baselines | Crop-level | Institutional Guidelines | Crop profiles, calendars, water requirements, sensitivity (requires local verification) |

---

## 3. The Six Mandated Crops

All six crops are evaluated using regional agricultural knowledge base profiles (KAU PoP, ICAR) and observed agro-climatic context:
1. **Rice (*Oryza sativa*):** Core crop; high water requirement (1250–1668 mm across Virippu, Mundakan, and Puncha seasons).
2. **Groundnut (*Arachis hypogaea*):** Core crop; moderate water requirement (~510 mm). Sensitive to prolonged water stress and waterlogging. Active sowing Oct–Nov, harvest Jan–Feb (outside active season in May).
3. **Banana (*Musa paradisiaca*):** Core crop; high water requirement (1200–2200 mm). Sown in May–June / Sep–Oct.
4. **Coconut (*Cocos nucifera*):** Core crop; perennial crop active year-round with May–June planting window; moderate-to-high water requirement (1300–2300 mm equivalent, 40–100 L/palm/day).
5. **Tapioca / Cassava (*Manihot esculenta*):** Core crop; moderate water requirement (750–1000 mm over 9–10 months). High waterlogging sensitivity.
6. **Sugarcane (*Saccharum officinarum*):** Optional crop; high water requirement (1500–2500 mm over 10–12 months).

### Agronomic Limitations & Dimensionality Disclosures
- **Banana Calendar Discrepancy:** Member 4 agronomic documentation and local extension guidelines contain conflicting planting windows for Banana in Palakkad (some indicating May–June and September–October planting, while others report year-round planting with supplemental drip irrigation or alternate autumn windows). This discrepancy is retained transparently rather than artificially harmonized.
- **Water Requirement Unit Inconsistency:** Field crops (Rice, Groundnut, Tapioca, Sugarcane) express cumulative crop-cycle water demand in millimeter depth (e.g., 510 mm to 2500 mm over 3 to 12 months), whereas Coconut expresses demand in daily volumetric consumption per tree (40–100 L/palm/day). The decision support engine respects these distinct dimensional units and does not compare whole-cycle demands or volumetric rates directly against single-month rainfall totals.

---

## 4. REST API Specifications

### Baseline APIs
- `GET /api/monthly` — NASA POWER + SMAP monthly records (2020–2025) using genuine Member 3 SMAP observations.
- `GET /api/soil` — Static soil properties (pH, clay, SOC).
- `GET /api/yearly` — Yearly climate aggregates.
- `GET /api/seasonal` — Seasonal summaries across 4 standard seasons.
- `GET /api/smap-daily` — Daily simulated SMAP proxy series (`SIMULATED_DAILY_PROXY` derived from NASA POWER GWETROOT; explicitly not actual daily satellite observations).

### Decision Support & Simulator APIs
- `GET /api/decision-support/overview` — Spatial coordinates, source registry, and catalog metadata.
- `GET /api/decision-support/crops` — Full profiles, water requirements, calendars, and sensitivity rules for all 6 crops.
- `GET /api/decision-support/suitability?month=<1-12>` — Comprehensive suitability evaluation for all 6 crops.
- `GET /api/decision-support/suitability/<crop_id>?month=<1-12>` — Single crop suitability evaluation.
- `GET /api/decision-support/climate-history` — Full historical records, top rainfall days, and dry periods.
- `GET /api/decision-support/risk-assessment` — 72-record risk assessment table with 7+ day dry spell and heavy rain flags.
- `GET /api/decision-support/data-quality` — Automated data ingestion validation report.
- `POST /api/decision-support/simulate` — Runs What-if Climate Scenario Simulation on isolated baseline copies.
- `POST /api/decision-support/compare-scenarios` — Batch compares multiple user scenarios against baseline.

---

## 5. Local Development & Testing

### Installation
```bash
git clone https://github.com/Sreejith-Vijayan/agroverse.git
cd agroverse
python -m pip install -r requirements.txt
```

### Running Test Suite
```bash
python -m pytest tests/test_agroverse_integration.py
```

### Starting Application
```bash
python app.py
```
Open [http://localhost:5000](http://localhost:5000) in your web browser.

### Deploying to Render

This repository includes a Render Blueprint in `render.yaml`. In Render, choose
**New + → Blueprint**, connect this repository, and apply the `agroverse` web
service. Render installs `requirements.txt` and starts the app with Gunicorn
bound to Render's assigned port. The `/healthz` endpoint is used for health
checks.

The app's datasets are included in the repository. Render's filesystem is
ephemeral, so the optional NASA POWER response cache may be recreated after a
restart; if the upstream service is unavailable, the dashboard uses its
documented demo-data fallback.

---

## 6. Scientific Transparency & Disclaimers

1. **No Data Fabrication:** Missing values and -9999 invalid satellite flags are preserved as `null`. They are never converted to zero.
2. **No Guaranteed Crop Success:** Evaluated statuses ("Suitable for further consideration", "Needs careful evaluation", "Potentially unsuitable") are exploratory screening classifications based on observed conditions. Local on-farm variables (drainage, irrigation availability, variety selection) must be validated in-situ.
3. **What-If Sensitivity Simulation:** The simulator conducts hypothetical sensitivity analyses on memory-isolated baseline data. It does not generate meteorological weather forecasts. Monthly rainfall adjustments do not replicate daily rainfall intensity distributions. Satellite soil moisture is kept at baseline without unvalidated physical fabrication.
