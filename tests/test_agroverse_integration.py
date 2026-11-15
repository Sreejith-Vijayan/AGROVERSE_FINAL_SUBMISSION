"""
Automated Integration and Unit Tests for AGROVERSE Platform
Tests Decision Support Engine, What-if Scenario Simulator, Data Validator,
and all original & new Flask API endpoints.
"""
import pytest
import json
from app import app
from decision_support import (
    DataLoader,
    DataValidator,
    ClimateAnalyzer,
    CropSuitabilityEngine,
    ScenarioSimulator,
    HistoricalAnalytics,
    CROPS_CATALOG,
    LOCATIONS
)

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

# ----------------- 1. Data Validation Tests -----------------
def test_data_validation():
    loader = DataLoader()
    validator = DataValidator(loader)
    report = validator.run_full_validation()
    assert report["status"] in ["PASSED", "PASSED_WITH_WARNINGS"]
    assert report["passed_checks"] >= 90
    assert len(report["errors"]) == 0
    assert "crops_integrity" in report["details"]
    assert len(report["details"]["crops_integrity"]["found_crops"]) == 6

# ----------------- 2. Crop Suitability Engine Tests -----------------
def test_crop_suitability_all_six_crops():
    loader = DataLoader()
    analyzer = ClimateAnalyzer(loader)
    engine = CropSuitabilityEngine(loader, analyzer)

    results = engine.evaluate_all_crops(target_month=5)
    assert len(results) == 6
    crop_ids = [r.crop_id for r in results]
    assert set(crop_ids) == {"rice", "groundnut", "banana", "coconut", "tapioca", "sugarcane"}

    for r in results:
        assert r.suitability_status in [
            "Suitable for further consideration",
            "Needs careful evaluation",
            "Potentially unsuitable under observed conditions",
            "Insufficient data for assessment"
        ]
        assert r.crop_name is not None
        assert len(r.missing_information) > 0
        assert r.verification_status in ["verified", "verified_numerical"]
        assert len(r.explanation) > 20
        assert 0.0 <= r.comparative_score <= 100.0

# ----------------- 3. What-if Simulator Tests -----------------
def test_scenario_simulator():
    loader = DataLoader()
    simulator = ScenarioSimulator(loader)
    sim_res = simulator.simulate(
        rainfall_pct_change=-25.0,
        temperature_delta_c=2.5,
        dry_spell_delta_days=10,
        target_month=5
    )

    assert "crop_comparisons" in sim_res
    assert len(sim_res["crop_comparisons"]) == 6
    assert sim_res["scenario_conditions"]["soil_moisture_status"] == "Preserved baseline (not fabricated)"
    assert sim_res["parameters"]["rainfall_pct_change"] == -25.0
    assert sim_res["parameters"]["temperature_delta_c"] == 2.5
    assert sim_res["parameters"]["dry_spell_delta_days"] == 10

    # Ensure baseline data is not modified
    base_summaries = simulator.analyzer.get_monthly_climate_summary(target_month=5)
    assert base_summaries[0]["average_rainfall_mm"] is not None

# ----------------- 4. Flask API Endpoints Tests -----------------
def test_original_api_endpoints(client):
    endpoints = ["/api/monthly", "/api/soil", "/api/yearly", "/api/seasonal", "/api/smap-daily"]
    for ep in endpoints:
        res = client.get(ep)
        assert res.status_code == 200
        data = json.loads(res.data)
        assert "data" in data or "properties" in data

def test_new_decision_support_endpoints(client):
    res_overview = client.get("/api/decision-support/overview")
    assert res_overview.status_code == 200
    ov_data = json.loads(res_overview.data)
    assert ov_data["status"] == "success"
    assert "spatial_locations" in ov_data
    assert "palakkad_demo_farm" in ov_data["spatial_locations"]
    assert "palakkad_town_district" in ov_data["spatial_locations"]

    res_crops = client.get("/api/decision-support/crops")
    assert res_crops.status_code == 200
    crops_data = json.loads(res_crops.data)
    assert crops_data["total_crops"] == 6

    res_suit = client.get("/api/decision-support/suitability?month=5")
    assert res_suit.status_code == 200
    suit_data = json.loads(res_suit.data)
    assert len(suit_data["results"]) == 6

    res_single = client.get("/api/decision-support/suitability/rice?month=5")
    assert res_single.status_code == 200
    single_data = json.loads(res_single.data)
    assert single_data["result"]["crop_id"] == "rice"

    res_hist = client.get("/api/decision-support/climate-history")
    assert res_hist.status_code == 200

    res_risk = client.get("/api/decision-support/risk-assessment")
    assert res_risk.status_code == 200

    res_quality = client.get("/api/decision-support/data-quality")
    assert res_quality.status_code == 200

def test_simulation_post_endpoint(client):
    payload = {
        "rainfall_pct_change": -20.0,
        "temperature_delta_c": 1.5,
        "dry_spell_delta_days": 8,
        "target_month": 5
    }
    res = client.post("/api/decision-support/simulate", json=payload)
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["status"] == "success"
    assert len(data["simulation"]["crop_comparisons"]) == 6

def test_compare_scenarios_post_endpoint(client):
    payload = {
        "target_month": 5,
        "scenarios": [
            {"name": "Drought Scenario", "rainfall_pct_change": -30.0, "temperature_delta_c": 2.0, "dry_spell_delta_days": 12},
            {"name": "Wet Scenario", "rainfall_pct_change": 25.0, "temperature_delta_c": -0.5, "dry_spell_delta_days": -4}
        ]
    }
    res = client.post("/api/decision-support/compare-scenarios", json=payload)
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["scenarios_evaluated"] == 2

def test_endpoint_input_validation(client):
    # Invalid month parameter returns 400
    res_inv_month = client.get("/api/decision-support/suitability?month=13")
    assert res_inv_month.status_code == 400

    res_inv_month_str = client.get("/api/decision-support/suitability?month=abc")
    assert res_inv_month_str.status_code == 400

    # Invalid crop_id returns 404
    res_inv_crop = client.get("/api/decision-support/suitability/unknown_crop?month=5")
    assert res_inv_crop.status_code == 404

    # Invalid simulate payload returns 400
    res_sim_invalid = client.post("/api/decision-support/simulate", json={"target_month": 15})
    assert res_sim_invalid.status_code == 400

    # Empty compare scenarios list returns 400
    res_comp_empty = client.post("/api/decision-support/compare-scenarios", json={"scenarios": [], "target_month": 5})
    assert res_comp_empty.status_code == 400

