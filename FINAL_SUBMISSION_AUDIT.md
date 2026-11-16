# AGROVERSE — Final Submission Technical Audit

**Audit Date:** November 15, 2026  
**Project:** AGROVERSE — NASA Data-Driven Agricultural Decision Support System  
**Target Challenge:** NASA Space Apps Challenge 2026 — *Field Shift: Adapting Farms with NASA Data*  
**Target Site:** Palakkad Demo Farm, Chittur-Kollengode Agricultural Corridor, Kerala, India  
**Coordinates:** 10.7080° N, 76.6390° E

---

## 1. Overall Submission Readiness

### Status: READY WITH LIMITATIONS

The project has achieved technical and scientific stability based on the recorded final verification results.

The verification included:

- 8 integration and unit tests, all passing.
- 19 primary API endpoint and input-validation checks.
- Flask dashboard rendering and static JavaScript syntax validation.
- Six-crop suitability assessment.
- What-If scenario simulation and comparison.
- NASA data provenance and scientific integrity checks.
- Automated data validation covering 157 checks.

The project is classified as **READY WITH LIMITATIONS** to maintain scientific transparency.

NASA POWER and SMAP provide regional-scale observations rather than farm-level measurements. The approximate 36 km SMAP resolution, 0.5° NASA POWER resolution, and absence of variety-specific crop-stage thermal thresholds limit the precision of farm-level recommendations.

These limitations are documented rather than presented as verified farm-level predictions.

---

## 2. Flask Application Startup

- **Startup Command:** `python app.py`
- **Framework:** Flask 3.0+
- **Python Version:** Python 3.11.9
- **Host:** `0.0.0.0`
- **Port:** `5000`
- **Local URL:** `http://127.0.0.1:5000`

### Runtime Dependencies

The application uses the following primary dependencies:

- Flask
- pandas
- numpy
- gunicorn
- pytest
- requests

### Import and Runtime Integrity

The recorded verification confirmed:

- `app.py` imports without errors.
- Required dependencies were available in the tested environment.
- No unhandled runtime exceptions occurred during module initialization or server startup.

**Verification Status: PASS**

---

## 3. Dashboard and UI Verification

### Testing Methods

The following verification methods were used:

- Flask WSGI test client rendering and HTTP response validation.
- Main dashboard response validation (`GET /` returned HTTP 200).
- HTML response size: 109,286 bytes.
- JavaScript syntax validation using Node.js:
  - `node -c static/dashboard.js`
  - `node -c static/dataService.js`
- Static asset linking verification.
- Leaflet CSS and JavaScript bundle integrity checks.

**Browser Automation Limitation:** Direct live browser interaction through DevTools was restricted by the local execution environment's network isolation. WSGI response validation and static JavaScript syntax verification were performed instead.

### Section Verification Checklist

| Dashboard Section | Verification |
|---|---|
| Overview Dashboard | PASS |
| Climate Dashboard | PASS |
| Soil Properties | PASS |
| SMAP Soil Moisture | PASS |
| Climate Trends & Seasonal | PASS |
| Risk Indicators | PASS |
| Rotation Strategy | PASS |
| Crop Decision Support | PASS |
| What-If Scenario Simulator | PASS |
| Historical Climate Logs | PASS |
| Data Quality & Sources | PASS |

### UI Verification Details

- Overview Dashboard: KPI cards, mini sparkbars and Leaflet demo farm map.
- Climate Dashboard: Historical NASA POWER climate trends.
- Soil Properties: Provisional pH, clay content and soil organic carbon cards.
- SMAP Soil Moisture: Member 3 monthly satellite observations and cloud-gap alert.
- Climate Trends: Yearly bar charts and seasonal breakdown cards.
- Risk Indicators: Dynamic metrics derived from available data.
- Rotation Strategy: Rice–Groundnut, Banana–Vegetables and Tapioca–Pulse rotations.
- Crop Decision Support: All six supported crops.
- What-If Simulator: Interactive sliders, parameter changes and comparison table.
- Historical Climate Logs: Rainfall extremes, temperature and dry-spell records.
- Data Quality & Sources: Automated validation report and spatial coordinate information.

### UI Labeling and Scientific Presentation

Misleading labels such as "Optimal Observation Level" and "High-Confidence Months" were replaced with descriptive regional coverage information.

The 35°C day and heavy rainfall indicators are presented as observational indicators, not guaranteed flood or crop-stress predictions.

**Verification Status: PASS**

---

## 4. API Endpoint Verification

The recorded API verification covered 19 primary routes and input-validation scenarios.

| Method | Endpoint | Expected | Actual | Description | Result |
|---|---|---:|---:|---|---|
| GET | `/` | 200 | 200 | Main Dashboard HTML | PASS |
| GET | `/api/decision-support/overview` | 200 | 200 | Spatial metadata, sources and six-crop catalog | PASS |
| GET | `/api/decision-support/crops` | 200 | 200 | Crop profiles, calendars, water requirements and sensitivities | PASS |
| GET | `/api/decision-support/suitability` | 200 | 200 | All six crops evaluated for May | PASS |
| GET | `/api/decision-support/suitability/rice` | 200 | 200 | Individual rice suitability evaluation | PASS |
| GET | `/api/decision-support/climate-history` | 200 | 200 | Historical climate observations | PASS |
| GET | `/api/decision-support/risk-assessment` | 200 | 200 | 72 monthly risk records | PASS |
| GET | `/api/decision-support/data-quality` | 200 | 200 | 157 automated validation checks | PASS |
| GET | `/api/monthly` | 200 | 200 | 72 monthly climate and SMAP records | PASS |
| GET | `/api/soil` | 200 | 200 | Soil physical properties | PASS |
| GET | `/api/yearly` | 200 | 200 | Six yearly climate summaries (2020–2025) | PASS |
| GET | `/api/seasonal` | 200 | 200 | 24 seasonal climate summaries | PASS |
| GET | `/api/smap-daily` | 200 | 200 | 2,192 daily proxy records | PASS |
| GET | `/api/decision-support/suitability` | 400 | 400 | Invalid month (`month=13`) | PASS |
| GET | `/api/decision-support/suitability/wheat` | 404 | 404 | Unsupported crop | PASS |
| POST | `/api/decision-support/simulate` | 200 | 200 | Valid scenario simulation | PASS |
| POST | `/api/decision-support/simulate` | 400 | 400 | Invalid target month | PASS |
| POST | `/api/decision-support/compare-scenarios` | 200 | 200 | Multiple named scenarios | PASS |
| POST | `/api/decision-support/compare-scenarios` | 400 | 400 | Empty scenario list | PASS |

**Verification Status: PASS**

---

## 5. Pytest Execution Results

**Command:**

```bash
python -m pytest -v
```

### Recorded Test Results

```text
============================= test session starts =============================

collecting ... collected 8 items

tests/test_agroverse_integration.py::test_data_validation PASSED
tests/test_agroverse_integration.py::test_crop_suitability_all_six_crops PASSED
tests/test_agroverse_integration.py::test_scenario_simulator PASSED
tests/test_agroverse_integration.py::test_original_api_endpoints PASSED
tests/test_agroverse_integration.py::test_new_decision_support_endpoints PASSED
tests/test_agroverse_integration.py::test_simulation_post_endpoint PASSED
tests/test_agroverse_integration.py::test_compare_scenarios_post_endpoint PASSED
tests/test_agroverse_integration.py::test_endpoint_input_validation PASSED

============================== 8 passed in 0.91s ==============================
```

### Test Summary

| Metric | Result |
|---|---:|
| Total Tests | 8 |
| Passed | 8 |
| Failed | 0 |
| Execution Time | 0.91 seconds |

**Verification Status: PASS**

---

## 6. Six-Crop Suitability Assessment

The six-crop suitability assessment was evaluated using:

`CropSuitabilityEngine.evaluate_all_crops(target_month=5)`

The following results represent the recorded May seasonal baseline.

| Crop | MVP Priority | Suitability Status | Score | Phenological Alignment |
|---|---|---|---:|---|
| Rice | Core | Needs careful evaluation | 45.0 | Virippu; April–May sowing |
| Groundnut | Core | Needs careful evaluation | 20.0 | Outside cycle; October sowing |
| Banana | Core | Needs careful evaluation | 45.0 | Variety-dependent; May–June planting |
| Coconut | Core | Suitable for further consideration | 60.0 | Perennial; active year-round |
| Tapioca / Cassava | Core | Needs careful evaluation | 45.0 | April–May seasonal planting |
| Sugarcane | Optional | Needs careful evaluation | 25.0 | Outside cycle; December–January sowing |

### Agronomic Accuracy Checks

- Groundnut is not incorrectly presented as actively growing in May. Its status changes in October to reflect the documented Rabi sowing period.
- Coconut is recognized as a perennial crop. Its May–June period is labeled as a planting window rather than a conventional sowing period.
- Crop-cycle water requirements retain their original units and are not directly compared with single-month rainfall.
- Qualitative sensitivities marked as `unknown` in the Member 4 knowledge base do not create unsupported risk penalties.
- Crop suitability scores are treated as exploratory screening indicators rather than guaranteed yield predictions.

**Verification Status: PASS**

---

## 7. What-If Scenario Simulator Verification

The What-If Simulator supports exploratory evaluation of changes in rainfall, temperature and dry-spell conditions.

### Sensitivity Modeling

- Percentage rainfall changes and temperature/dry-spell deltas are evaluated on isolated in-memory copies.
- Baseline observations are not mutated during simulation.
- Arbitrary fallback values (`100.0 mm`, `28.0 °C`, and `5 days`) were removed.
- Missing baseline observations remain `None` and are accompanied by availability information.

### Scientific Integrity

- Root-zone soil moisture is held at its baseline value.
- The simulator does not fabricate new satellite soil-moisture observations.
- Heavy-rain frequency preserves empirical baseline frequency rather than applying unsupported thresholds to monthly totals.

### Input Validation

The simulator enforces the following recorded parameter ranges:

| Parameter | Accepted Range |
|---|---|
| Rainfall change | -100% to +300% |
| Temperature change | -10°C to +15°C |
| Dry-spell change | -60 to +90 days |
| Target month | 1 to 12 |

Invalid inputs return HTTP 400 responses with descriptive validation errors.

### Multi-Scenario Comparison

The `/api/decision-support/compare-scenarios` endpoint evaluates multiple named scenarios and returns structured score differences and risk transitions.

**Verification Status: PASS**

---

## 8. NASA Data Provenance and Scientific Integrity

| Scientific Integrity Check | Status | Implementation Detail |
|---|---|---|
| Genuine vs simulated NASA data | PASS | Monthly SMAP records use actual Member 3 satellite aggregations. Secondary modeled fields and daily proxies are explicitly labeled as simulated. |
| SMAP resolution disclosure | PASS | Approximate 36 km coarse-grid limitation is documented. |
| Historical data vs forecast | PASS | NASA POWER observations are identified as historical 2020–2025 climate context. |
| Missing-value preservation | PASS | Empty strings, `-9999` and `-9999.0` are mapped to missing values. Genuine zero-rain observations remain zero. |
| Spatial coordinate provenance | PASS | Demo farm and Palakkad Town coordinates are maintained separately. |
| Crop water comparability | PASS | Crop-cycle water requirements are not claimed to be satisfied by single-month rainfall. |
| Exploratory suitability scoring | PASS | Scores are documented as software screening indices, not guaranteed agronomic predictions. |
| Removal of unjustified verification claims | PASS | Unsupported blanket verification labels and hardcoded fallback statistics were removed. |
| Daily SMAP proxy disclosure | PASS | Daily proxy API metadata identifies `SIMULATED_DAILY_PROXY`. |
| Documentation transparency | PASS | README documents proxy data, crop-calendar discrepancies and water-unit differences. |

### Important Data Provenance Details

**SMAP Observations**

Monthly SMAP observations from Member 3 are identified as:

`MEMBER_3_SMAP_OBSERVATION`

The data are presented as regional satellite context, not farm-level in-situ soil moisture measurements.

**Simulated Daily Proxy**

The `/api/smap-daily` endpoint identifies its data type as:

`SIMULATED_DAILY_PROXY`

These daily values are derived from NASA POWER GWETROOT and must not be interpreted as genuine daily SMAP satellite observations.

**Spatial Coordinates**

The project maintains two distinct locations:

- Palakkad Demo Farm / Chittur-Kollengode corridor / NASA POWER extraction site: `10.7080° N, 76.6390° E`
- Palakkad Town / District centroid: `10.7867° N, 76.6548° E`

These coordinates are not treated as interchangeable.

**Crop Water Requirements**

Field-crop water requirements expressed in millimeters and coconut water requirements expressed in liters per palm per irrigation are retained in their native units. They are not directly compared.

**Verification Status: PASS**

---

## 9. Remaining Limitations and Known Issues

### Critical Issues

No critical blockers were identified in the recorded final verification.

### Known Data and Scientific Limitations

**1. Coarse Satellite Resolution**

NASA POWER (approximately 0.5° × 0.625°) and SMAP (approximately 36 km) cannot represent all field-level variations, including micro-topography, soil compaction and local drainage conditions.

**2. Growth-Stage Thermal Thresholds**

The Member 4 knowledge base contains qualitative temperature sensitivities but does not provide complete variety-specific thermal degree-day equations.

**3. Secondary Meteorological Proxies**

Relative humidity, solar radiation and wind speed in the handover JSON are empirical parametric models rather than direct local weather-station observations.

**4. Banana Crop Calendar**

Regional guidelines contain differing planting-window recommendations, including May–June / September–October and year-round irrigated cultivation. Local validation is required.

**5. Crop Water Unit Differences**

Field-crop requirements are expressed as water depth in millimeters, whereas coconut requirements use liters per palm per day or irrigation. These measurements are not directly comparable.

These limitations are disclosed to avoid presenting regional or modeled information as precise farm-level measurements.

---

## 10. Major Files Modified During Final Corrections

The following files were included in the recorded final correction process:

| File | Changes |
|---|---|
| `app.py` | Conditional data-source banner and simulated daily proxy metadata |
| `static/dashboard.js` | Improved scientific labeling and dynamic crop verification status |
| `templates/index.html` | Dynamic coverage label and demo-data warning presentation |
| `README.md` | Data provenance, simulated proxy disclosure and crop-calendar documentation |
| `decision_support/data_validator.py` | Automated data validation across 157 checks |
| `tests/test_agroverse_integration.py` | Eight integration tests and input-boundary validation |
| `FINAL_SUBMISSION_AUDIT.md` | Final verification evidence and documented limitations |

---

## 11. Recommended Demonstration Flow

The following walkthrough is recommended for demonstrating the final application.

### Step 1: Launch the Application

```bash
python app.py
```

Open:

`http://localhost:5000`

### Step 2: Dashboard Walkthrough

Navigate through:

- Overview
- Climate
- SMAP
- Climate Trends
- Risk Indicators

Highlight the climate observations, soil information and data-source disclosures.

### Step 3: Crop Decision Support

Demonstrate the six supported crops.

Suggested months:

- **May (Month 5):** Highlight Coconut and Virippu Rice.
- **October (Month 10):** Demonstrate Groundnut's documented Rabi sowing period.

### Step 4: What-If Simulator

Use example parameter changes:

- Rainfall: -25%
- Temperature: +2.0°C
- Dry spell: +10 days

Show how the simulator evaluates changes against the baseline.

### Step 5: Scenario Comparison

Click **Compare Pre-set Scenarios** to demonstrate multi-scenario evaluation.

### Step 6: Data Quality and Sources

Finish by showing the data-quality section, automated validation information and the scientific limitations of the underlying datasets.

---

## 12. Final Submission Checklist

- [ ] Verify `.gitignore` excludes `.venv/`, `.pytest_cache/` and `__pycache__/`.
- [ ] Ensure `README.md` is available at the repository root.
- [ ] Ensure `requirements.txt` is available at the repository root.
- [ ] Verify application startup using `python app.py`.
- [ ] Verify all eight integration tests in the final environment.
- [ ] Ensure Member 3 and Member 4 data files are included.
- [ ] Ensure simulated data and regional satellite limitations are clearly disclosed.
- [ ] Ensure all required frontend, backend and decision-support modules are included.
- [ ] Confirm the final GitHub repository contains the intended submission files.

---

## Final Assessment

**Overall Status: READY WITH LIMITATIONS**

AGROVERSE integrates historical NASA climate observations, satellite-derived soil-moisture information, agricultural knowledge and an exploratory crop decision-support engine into a unified web application.

The system includes six-crop suitability assessment, historical climate analysis, risk indicators, crop rotation information, a What-If simulator and multi-scenario comparison.

Its scientific limitations are explicitly documented, particularly the coarse spatial resolution of satellite products, simulated secondary meteorological fields and the exploratory nature of crop suitability scoring.

The recorded final verification results indicate successful application startup, eight passing tests, nineteen API verification scenarios and 157 automated data-validation checks.

**AGROVERSE is prepared for final demonstration and submission, subject to the documented data limitations and final-environment verification.**
