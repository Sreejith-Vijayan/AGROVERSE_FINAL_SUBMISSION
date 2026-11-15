import datetime as dt, json, os
from flask import Flask, render_template, request, jsonify
import pandas as pd
import data, charts, climate, data_source

# Import Decision Support components
from decision_support import (
    DataLoader,
    DataValidator,
    ClimateAnalyzer,
    CropSuitabilityEngine,
    ScenarioSimulator,
    HistoricalAnalytics,
    LOCATIONS,
    SOURCE_REGISTRY_METADATA,
    CROPS_CATALOG
)

app = Flask(__name__)
DATASET_START = pd.Timestamp("2020-01-01")
DATASET_END = pd.Timestamp("2025-12-31")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_DIR = os.path.join(BASE_DIR, "07_UI_HANDOVER", "json")

# Initialize Decision Support singletons
ds_loader = DataLoader()
ds_validator = DataValidator(ds_loader)
ds_analyzer = ClimateAnalyzer(ds_loader)
ds_suitability = CropSuitabilityEngine(ds_loader, ds_analyzer)
ds_simulator = ScenarioSimulator(ds_loader, ds_suitability)
ds_historical = HistoricalAnalytics(ds_loader)


def load_handover_json(filename):
    path = os.path.join(JSON_DIR, filename)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"meta": {}, "data": []}


def _parse(s):
    try:
        return pd.Timestamp(s) if s else None
    except Exception:
        return None


# ====================================================================
# ORIGINAL REST API ENDPOINTS (07_UI_HANDOVER Integration)
# ====================================================================

@app.route("/api/monthly")
def api_monthly():
    payload = load_handover_json("monthly_climate_smap.json")
    from_date = request.args.get("from")
    to_date = request.args.get("to")
    if from_date or to_date:
        filtered = []
        for row in payload.get("data", []):
            ym = row.get("year_month")
            if from_date and ym < from_date:
                continue
            if to_date and ym > to_date:
                continue
            filtered.append(row)
        return jsonify({"meta": payload.get("meta", {}), "data": filtered})
    return jsonify(payload)


@app.route("/api/soil")
def api_soil():
    return jsonify(load_handover_json("static_soil_properties.json"))


@app.route("/api/yearly")
def api_yearly():
    return jsonify(load_handover_json("yearly_climate_summary.json"))


@app.route("/api/seasonal")
def api_seasonal():
    return jsonify(load_handover_json("seasonal_climate_summary.json"))


@app.route("/api/smap-daily")
def api_smap_daily():
    csv_path = os.path.join(BASE_DIR, "07_UI_HANDOVER", "csv", "smap_daily_cleaned.csv")
    if os.path.exists(csv_path):
        df_daily = pd.read_csv(csv_path)
        from_date = request.args.get("from")
        to_date = request.args.get("to")
        if from_date:
            df_daily = df_daily[df_daily["date"] >= from_date]
        if to_date:
            df_daily = df_daily[df_daily["date"] <= to_date]
        return jsonify({
            "meta": {
                "data_type": "SIMULATED_DAILY_PROXY",
                "source_disclaimer": "This daily soil moisture series contains SIMULATED_DAILY_PROXY values derived from NASA POWER GWETROOT and must not be interpreted as actual daily SMAP observations. Genuine satellite SMAP observations are available only at the monthly aggregate level from Member 3.",
                "location": "Palakkad Demo Farm, Kerala (10.7080° N, 76.6390° E)",
                "resolution": "Simulated point proxy (~36 km grid cell reference; not a farm-level measurement)",
                "status": "SIMULATED_DEMO",
                "records": len(df_daily)
            },
            "data": df_daily.to_dict(orient="records")
        })
    return jsonify({
        "meta": {
            "data_type": "SIMULATED_DAILY_PROXY",
            "source_disclaimer": "This daily soil moisture series contains SIMULATED_DAILY_PROXY values and must not be interpreted as actual daily SMAP observations.",
            "records": 0
        },
        "data": []
    })


# ====================================================================
# NEW DECISION SUPPORT & SCENARIO REST API ENDPOINTS
# ====================================================================

@app.route("/api/decision-support/overview")
def api_ds_overview():
    """Returns metadata, source registry, and spatial location definitions."""
    return jsonify({
        "status": "success",
        "spatial_locations": LOCATIONS,
        "source_registry": SOURCE_REGISTRY_METADATA,
        "crops_catalog": CROPS_CATALOG,
        "coverage": {
            "start": "2020-01-01",
            "end": "2025-12-31",
            "note": "Empirical observational records; zero artificial extrapolation for unsupported dates."
        }
    })


@app.route("/api/decision-support/crops")
def api_ds_crops():
    """Returns profiles, water requirements, calendars and sensitivity for all 6 crops."""
    profiles = ds_loader.load_crop_profiles()
    calendars = ds_loader.load_crop_calendar()
    water_reqs = ds_loader.load_crop_water_requirements()
    sensitivities = ds_loader.load_crop_climate_sensitivity()
    
    crops_data = []
    for p in profiles:
        cid = p.get("crop_id")
        crops_data.append({
            "profile": p,
            "calendars": [c for c in calendars if c.get("crop_id") == cid],
            "water_requirements": next((w for w in water_reqs if w.get("crop_id") == cid), {}),
            "sensitivities": [s for s in sensitivities if s.get("crop_id") == cid]
        })
    return jsonify({
        "status": "success",
        "total_crops": len(crops_data),
        "crops": crops_data
    })


@app.route("/api/decision-support/suitability")
def api_ds_suitability():
    """Evaluates crop suitability for a selected month (1-12)."""
    month_str = request.args.get("month", "5")
    try:
        month = int(month_str)
        if month < 1 or month > 12:
            return jsonify({
                "status": "error",
                "message": f"Invalid month: {month_str}. Must be an integer between 1 and 12."
            }), 400
    except (ValueError, TypeError):
        return jsonify({
            "status": "error",
            "message": f"Invalid month parameter: '{month_str}'. Must be an integer between 1 and 12."
        }), 400

    results = ds_suitability.evaluate_all_crops(target_month=month)
    return jsonify({
        "status": "success",
        "month": month,
        "results": [r.to_dict() for r in results]
    })


@app.route("/api/decision-support/suitability/<crop_id>")
def api_ds_suitability_crop(crop_id):
    """Evaluates suitability for an individual crop."""
    valid_crops = {"rice", "groundnut", "banana", "coconut", "tapioca", "sugarcane"}
    if crop_id not in valid_crops:
        return jsonify({
            "status": "error",
            "message": f"Unknown crop '{crop_id}'. Supported crops: {sorted(list(valid_crops))}."
        }), 404

    month_str = request.args.get("month", "5")
    try:
        month = int(month_str)
        if month < 1 or month > 12:
            return jsonify({
                "status": "error",
                "message": f"Invalid month: {month_str}. Must be an integer between 1 and 12."
            }), 400
    except (ValueError, TypeError):
        return jsonify({
            "status": "error",
            "message": f"Invalid month parameter: '{month_str}'. Must be an integer between 1 and 12."
        }), 400

    res = ds_suitability.evaluate_crop(crop_id, target_month=month)
    return jsonify({
        "status": "success",
        "month": month,
        "result": res.to_dict()
    })


@app.route("/api/decision-support/climate-history")
def api_ds_climate_history():
    """Returns integrated Member 3 climate history tables and event logs."""
    history = ds_historical.get_full_climate_history()
    return jsonify({
        "status": "success",
        "climate_history": history
    })


@app.route("/api/decision-support/risk-assessment")
def api_ds_risk_assessment():
    """Returns Member 3 integrated risk assessment dataset."""
    risk_data = ds_historical.get_integrated_risk_assessment()
    return jsonify({
        "status": "success",
        "risk_assessment": risk_data
    })


@app.route("/api/decision-support/data-quality")
def api_ds_data_quality():
    """Returns the automated data validation and quality report."""
    report = ds_validator.run_full_validation()
    return jsonify({
        "status": "success",
        "quality_report": report
    })


@app.route("/api/decision-support/simulate", methods=["POST"])
def api_ds_simulate():
    """
    Simulates hypothetical scenario changes:
    - rainfall_pct_change: percentage (-100 to +300)
    - temperature_delta_c: delta in °C (-10 to +15)
    - dry_spell_delta_days: change in days (-60 to +90)
    - target_month: integer (1 to 12)
    """
    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({
            "status": "error",
            "message": "Invalid JSON payload or missing Content-Type: application/json."
        }), 400
    if not isinstance(payload, dict):
        return jsonify({
            "status": "error",
            "message": "Payload must be a JSON object."
        }), 400

    try:
        rain_pct = float(payload.get("rainfall_pct_change", 0.0))
        temp_delta = float(payload.get("temperature_delta_c", 0.0))
        dry_delta = int(payload.get("dry_spell_delta_days", 0))
        target_month_raw = payload.get("target_month", 5)
        target_month = int(target_month_raw)
        if target_month < 1 or target_month > 12:
            return jsonify({
                "status": "error",
                "message": f"Invalid target_month: {target_month_raw}. Must be an integer between 1 and 12."
            }), 400
    except (ValueError, TypeError):
        return jsonify({
            "status": "error",
            "message": "Invalid simulation parameters. Expected numerical values."
        }), 400

    sim_result = ds_simulator.simulate(
        rainfall_pct_change=rain_pct,
        temperature_delta_c=temp_delta,
        dry_spell_delta_days=dry_delta,
        target_month=target_month
    )
    if sim_result.get("status") == "ValidationError":
        return jsonify({
            "status": "error",
            "errors": sim_result.get("errors", [])
        }), 400

    return jsonify({
        "status": "success",
        "simulation": sim_result
    })


@app.route("/api/decision-support/compare-scenarios", methods=["POST"])
def api_ds_compare_scenarios():
    """Compares multiple user scenarios against baseline."""
    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({
            "status": "error",
            "message": "Invalid JSON payload or missing Content-Type: application/json."
        }), 400
    if not isinstance(payload, dict):
        return jsonify({
            "status": "error",
            "message": "Payload must be a JSON object."
        }), 400

    scenarios = payload.get("scenarios")
    if not isinstance(scenarios, list) or len(scenarios) == 0:
        return jsonify({
            "status": "error",
            "message": "Payload must include a non-empty 'scenarios' list."
        }), 400

    target_month_raw = payload.get("target_month", 5)
    try:
        target_month = int(target_month_raw)
        if target_month < 1 or target_month > 12:
            return jsonify({
                "status": "error",
                "message": f"Invalid target_month: {target_month_raw}. Must be an integer between 1 and 12."
            }), 400
    except (ValueError, TypeError):
        return jsonify({
            "status": "error",
            "message": f"Invalid target_month: '{target_month_raw}'. Must be an integer between 1 and 12."
        }), 400

    comparisons = []
    for idx, sc in enumerate(scenarios):
        if not isinstance(sc, dict):
            return jsonify({
                "status": "error",
                "message": f"Scenario at index {idx} must be a JSON object."
            }), 400
        try:
            r_pct = float(sc.get("rainfall_pct_change", 0.0))
            t_delta = float(sc.get("temperature_delta_c", 0.0))
            d_delta = int(sc.get("dry_spell_delta_days", 0))
        except (ValueError, TypeError):
            return jsonify({
                "status": "error",
                "message": f"Scenario '{sc.get('name', idx)}' contains invalid numerical parameters."
            }), 400

        name = str(sc.get("name", f"Scenario {idx + 1}"))
        res = ds_simulator.simulate(
            rainfall_pct_change=r_pct,
            temperature_delta_c=t_delta,
            dry_spell_delta_days=d_delta,
            target_month=target_month
        )
        comparisons.append({
            "scenario_name": name,
            "simulation": res
        })

    return jsonify({
        "status": "success",
        "target_month": target_month,
        "scenarios_evaluated": len(comparisons),
        "comparisons": comparisons
    })


# ====================================================================
# MAIN DASHBOARD VIEW
# ====================================================================

@app.route("/healthz")
def health_check():
    return jsonify({"status": "ok"})


@app.route("/")
def overview():
    df, source = data_source.get_series(data.FARM["lat"], data.FARM["lon"])
    # Cap dataset observations at 2025-12-31 per verified handover dataset
    first, last = DATASET_START, DATASET_END
    msg = None

    # Location check
    farm_arg = request.args.get("farm")
    if farm_arg and farm_arg.lower() != "palakkad":
        msg = f"Palakkad Demo Farm is the primary verified site. For other locations ({farm_arg}) in 2022–2026, No Data Available."

    raw_s = request.args.get("start")
    raw_e = request.args.get("end")
    req_s, req_e = _parse(raw_s), _parse(raw_e)

    # Detect requested periods outside verified dataset (e.g. 2026 or future/unsupported)
    if req_s is not None and req_s > DATASET_END:
        msg = (msg + " " if msg else "") + "No Data Available for requested 2026 period. Verified observational dataset for Palakkad covers January 2020 to December 2025."
    elif req_e is not None and req_e > DATASET_END:
        msg = (msg + " " if msg else "") + "Verified observations cover January 2020 to December 2025; dates for 2026 show No Data Available. Adjusted to 31 Dec 2025."

    if req_s is None and req_e is None:
        # Default: 2020-01-01 to 2025-12-31 (full verified dataset)
        s, e = DATASET_START, DATASET_END
    else:
        s = req_s if req_s is not None else req_e
        e = req_e if req_e is not None else req_s
        if s > e: s, e = e, s
        if s < DATASET_START or e > DATASET_END:
            if not msg:
                msg = f"Data is available from {DATASET_START:%d %b %Y} to {DATASET_END:%d %b %Y}; your dates were adjusted."
            s, e = max(s, DATASET_START), min(e, DATASET_END)

    if source == "nasa_power":
        coverage_label = "NASA POWER Observational Series · January 2020 – December 2025"
    else:
        coverage_label = "DEMO / SIMULATED DATA · Offline Synthetic Climate Series"
    r = climate.analyze(df, s, e)
    k, c, tr = r["kpi"], r["change"], r["trend"]
    label = (f"{r['start']:%d %b %Y} – {r['end']:%d %b %Y}")
    if r["single"]:
        msg = (msg or "") + " One date selected: showing a 7-day window (±3 days) around it."

    presets = [
        ("2020 – 2025 (Full Record)", "2020-01-01", "2025-12-31"),
        ("Year 2025", "2025-01-01", "2025-12-31"),
        ("Year 2024", "2024-01-01", "2024-12-31"),
        ("Year 2023", "2023-01-01", "2023-12-31"),
        ("Year 2022", "2022-01-01", "2022-12-31"),
        ("Last 30 days (Dec 2025)", "2025-12-02", "2025-12-31"),
    ]

    # Handover JSON datasets
    monthly_payload = load_handover_json("monthly_climate_smap.json")
    soil_payload = load_handover_json("static_soil_properties.json")
    yearly_payload = load_handover_json("yearly_climate_summary.json")
    seasonal_payload = load_handover_json("seasonal_climate_summary.json")

    # Initial Decision Support & Risk Assessment data for server-side rendering support
    initial_crops_suitability = ds_suitability.evaluate_all_crops(target_month=5)
    quality_report = ds_validator.run_full_validation()

    return render_template(
        "index.html", farm=data.FARM, rotations=data.ROTATIONS, ndvi=data.NDVI,
        source=source, msg=msg, label=label, span=r["span"], presets=presets,
        coverage_label=coverage_label,
        start_val=r["start"].strftime("%Y-%m-%d") if not r["single"] else (r["start"] + pd.Timedelta(days=3)).strftime("%Y-%m-%d"),
        end_val=r["end"].strftime("%Y-%m-%d") if not r["single"] else (r["start"] + pd.Timedelta(days=3)).strftime("%Y-%m-%d"),
        min_date=first.strftime("%Y-%m-%d"), max_date=last.strftime("%Y-%m-%d"),
        k=k, risks=r["risks"], c=c, mode=tr["mode"],
        spark_rain=charts.sparkbars(k["rain_spark"], "#3a86c8"),
        spark_moist=charts.sparkline(k["soil_spark"], "#3f9b5b"),
        spark_veg=charts.sparkline(data.NDVI["line"], "#3f9b5b") if data.NDVI.get("line") else "",
        spark_heat=charts.sparkbars(k["heat_spark"], "#f0a030"),
        trends=charts.trends_chart(tr["labels"], tr["rain"], tr["soil"]),
        tmax_chart=charts.year_chart(c["years"], c["tmax"], "#d6453d", "Max temperature (°C)", c["sel_year"]),
        rain_chart=charts.year_chart(c["years"], c["rain"], "#3a86c8", "Rainfall (mm)", c["sel_year"]),
        heat_chart=charts.year_chart(c["years"], c["heat"], "#e0912c", "Days ≥ 35 °C", c["sel_year"]),
        monthly_data=monthly_payload,
        soil_data=soil_payload,
        yearly_data=yearly_payload,
        seasonal_data=seasonal_payload,
        initial_crops_suitability=[res.to_dict() for res in initial_crops_suitability],
        quality_report=quality_report,
        locations=LOCATIONS,
        source_registry=SOURCE_REGISTRY_METADATA
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
