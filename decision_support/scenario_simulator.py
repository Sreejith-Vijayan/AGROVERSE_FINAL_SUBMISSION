"""
decision_support.scenario_simulator
Interactive What-If Climate Scenario Simulator.

Simulates hypothetical alterations in rainfall, temperature, and dry spell duration
applied to isolated copies of baseline empirical data, without modifying underlying datasets.

Design principles:
- Missing baseline values are preserved as None, never replaced with arbitrary constants.
- Soil moisture dynamics are held at baseline; recalculating them from monthly rainfall
  would fabricate unvalidated physical data.
- The heavy-rain indicator is derived from the baseline empirical flag, not a hardcoded mm threshold.
- All scenario output is clearly labelled as a hypothetical sensitivity analysis.
"""
from typing import Dict, List, Any, Optional
from .data_loader import DataLoader
from .climate_analyzer import ClimateAnalyzer
from .crop_suitability import CropSuitabilityEngine

# Validated input bounds
_RAIN_PCT_MIN = -100.0
_RAIN_PCT_MAX = 300.0
_TEMP_DELTA_MIN = -10.0
_TEMP_DELTA_MAX = 15.0
_DRY_DELTA_MIN = -60
_DRY_DELTA_MAX = 90
_MONTH_MIN = 1
_MONTH_MAX = 12


def _validate_simulate_inputs(
    rainfall_pct_change: float,
    temperature_delta_c: float,
    dry_spell_delta_days: int,
    target_month: int,
) -> List[str]:
    """Return a list of validation error messages (empty = valid)."""
    errs = []
    if not (_RAIN_PCT_MIN <= rainfall_pct_change <= _RAIN_PCT_MAX):
        errs.append(
            f"rainfall_pct_change must be between {_RAIN_PCT_MIN} and {_RAIN_PCT_MAX}; "
            f"got {rainfall_pct_change}."
        )
    if not (_TEMP_DELTA_MIN <= temperature_delta_c <= _TEMP_DELTA_MAX):
        errs.append(
            f"temperature_delta_c must be between {_TEMP_DELTA_MIN} and {_TEMP_DELTA_MAX}; "
            f"got {temperature_delta_c}."
        )
    if not (_DRY_DELTA_MIN <= dry_spell_delta_days <= _DRY_DELTA_MAX):
        errs.append(
            f"dry_spell_delta_days must be between {_DRY_DELTA_MIN} and {_DRY_DELTA_MAX}; "
            f"got {dry_spell_delta_days}."
        )
    if not (_MONTH_MIN <= target_month <= _MONTH_MAX):
        errs.append(
            f"target_month must be an integer between {_MONTH_MIN} and {_MONTH_MAX}; "
            f"got {target_month}."
        )
    return errs


class ScenarioSimulator:
    def __init__(self, loader: DataLoader = None, engine: CropSuitabilityEngine = None):
        self.loader = loader or DataLoader()
        self.engine = engine or CropSuitabilityEngine(self.loader)
        self.analyzer = self.engine.analyzer

    def simulate(
        self,
        rainfall_pct_change: float = 0.0,
        temperature_delta_c: float = 0.0,
        dry_spell_delta_days: int = 0,
        target_month: int = 5,
    ) -> Dict[str, Any]:
        """
        Executes a hypothetical sensitivity simulation across all 6 crops.

        Rules:
        - Operates on isolated in-memory copies; underlying datasets are never mutated.
        - Missing baseline values are preserved as None; arbitrary fallback constants are
          never substituted (e.g. 100 mm, 28 °C, 5 dry-spell days).
        - The heavy-rain indicator is derived from the empirical baseline flag frequency,
          not from a hardcoded monthly mm threshold applied to the simulated rainfall.
        - Soil moisture observations are held at baseline; they cannot be recalculated
          reliably from a uniform rainfall percentage shift.
        - Inputs are validated; a ValidationError key is returned if bounds are exceeded.
        """
        # 1. Validate inputs
        validation_errors = _validate_simulate_inputs(
            rainfall_pct_change, temperature_delta_c, dry_spell_delta_days, target_month
        )
        if validation_errors:
            return {
                "status": "ValidationError",
                "errors": validation_errors,
                "parameters": {
                    "rainfall_pct_change": rainfall_pct_change,
                    "temperature_delta_c": temperature_delta_c,
                    "dry_spell_delta_days": dry_spell_delta_days,
                    "target_month": target_month,
                },
            }

        # 2. Fetch baseline empirical conditions for the target month
        monthly_summaries = self.analyzer.get_monthly_climate_summary(target_month=target_month)
        base_monthly = monthly_summaries[0] if monthly_summaries else {}
        base_risk = self.analyzer.get_risk_indicators_summary(month=target_month)

        # Preserve None for missing values — do NOT substitute arbitrary constants.
        base_rain_raw = base_monthly.get("average_rainfall_mm")
        base_temp_raw = base_monthly.get("average_temperature_c")
        base_dry_raw = base_risk.get("avg_longest_dry_spell_days")
        base_sm_am = base_monthly.get("soil_moisture_am")  # may be None — preserved

        # Availability flags (reported in output for transparency)
        rain_available = base_rain_raw is not None
        temp_available = base_temp_raw is not None
        dry_available = base_dry_raw is not None

        base_rain = float(base_rain_raw) if rain_available else None
        base_temp = float(base_temp_raw) if temp_available else None
        base_dry = int(base_dry_raw) if dry_available else None

        # 3. Compute hypothetical scenario conditions (isolated copies)
        # Only apply delta/scaling where baseline data exists.
        sim_rain = (
            round(max(0.0, base_rain * (1.0 + rainfall_pct_change / 100.0)), 2)
            if rain_available else None
        )
        sim_temp = (
            round(base_temp + temperature_delta_c, 2)
            if temp_available else None
        )
        sim_dry = (
            max(0, int(base_dry + dry_spell_delta_days))
            if dry_available else None
        )

        # Heavy-rain indicator for the scenario:
        # Use the empirical baseline heavy-rain frequency rate from the risk summary.
        # Do NOT infer it by comparing sim_rain against a hardcoded mm threshold.
        base_heavy_freq = base_risk.get("heavy_rain_months_frequency_pct", 0) or 0
        # Carry the same empirical flag rate into the scenario (we cannot reliably model
        # how a uniform rainfall shift changes daily extremes from monthly totals alone).
        sim_heavy_rain_indicator = base_heavy_freq > 30
        sim_heavy_rain_note = (
            "Heavy-rain indicator is based on observed empirical frequency from baseline data. "
            "It is not recalculated from the simulated monthly total, as uniform percentage "
            "rainfall shifts do not reliably reproduce changes in daily extreme event frequency."
        )

        # 4. Baseline evaluation
        baseline_results = self.engine.evaluate_all_crops(target_month=target_month)

        # 5. Scenario evaluation with isolated override
        # Only include keys where values are available to avoid overwriting real None values
        # with arbitrary stand-ins inside evaluate_crop().
        sim_override: Dict[str, Any] = {
            "heavy_rain_month_indicator": sim_heavy_rain_indicator,
            "AM_mean": base_sm_am,  # Preserved baseline; not fabricated
        }
        if sim_rain is not None:
            sim_override["rainfall_mm"] = sim_rain
        if sim_temp is not None:
            sim_override["average_temperature_c"] = sim_temp
        if sim_dry is not None:
            sim_override["longest_dry_spell_days"] = sim_dry

        scenario_results = self.engine.evaluate_all_crops(
            target_month=target_month, climate_override=sim_override
        )

        # 6. Build comparative diff for each crop
        crop_comparisons = []
        for b_res, s_res in zip(baseline_results, scenario_results):
            b_risks_set = set(b_res.risk_factors)
            s_risks_set = set(s_res.risk_factors)

            new_risks = list(s_risks_set - b_risks_set)
            reduced_risks = list(b_risks_set - s_risks_set)

            reasons = []
            if rainfall_pct_change != 0:
                if rain_available:
                    reasons.append(
                        f"Rainfall scaled by {rainfall_pct_change:+.1f}% "
                        f"({base_rain:.1f} mm → {sim_rain:.1f} mm)."
                    )
                else:
                    reasons.append(
                        f"Rainfall_pct_change requested ({rainfall_pct_change:+.1f}%) "
                        "but baseline rainfall data is unavailable."
                    )
            if temperature_delta_c != 0:
                if temp_available:
                    reasons.append(
                        f"Temperature shifted by {temperature_delta_c:+.1f} °C "
                        f"({base_temp:.1f} °C → {sim_temp:.1f} °C)."
                    )
                else:
                    reasons.append(
                        f"Temperature delta requested ({temperature_delta_c:+.1f} °C) "
                        "but baseline temperature data is unavailable."
                    )
            if dry_spell_delta_days != 0:
                if dry_available:
                    reasons.append(
                        f"Dry spell length altered by {dry_spell_delta_days:+d} days "
                        f"({base_dry} d → {sim_dry} d)."
                    )
                else:
                    reasons.append(
                        f"Dry spell delta requested ({dry_spell_delta_days:+d} days) "
                        "but baseline dry spell data is unavailable."
                    )
            if not reasons:
                reasons.append("Identical to baseline observational conditions.")

            crop_comparisons.append({
                "crop_id": b_res.crop_id,
                "crop_name": b_res.crop_name,
                "priority": b_res.priority,
                "baseline_status": b_res.suitability_status,
                "scenario_status": s_res.suitability_status,
                "status_changed": b_res.suitability_status != s_res.suitability_status,
                "baseline_score": b_res.comparative_score,
                "scenario_score": s_res.comparative_score,
                "score_delta": round(s_res.comparative_score - b_res.comparative_score, 1),
                "supporting_factors_baseline": b_res.supporting_factors,
                "supporting_factors_scenario": s_res.supporting_factors,
                "new_risks": new_risks,
                "reduced_risks": reduced_risks,
                "reasons_for_change": reasons,
                "missing_information": s_res.missing_information,
                "scenario_explanation": s_res.explanation,
            })

        return {
            "metadata": {
                "target_month": target_month,
                "month_name": base_monthly.get("month_name", f"Month {target_month}"),
                "disclaimer": (
                    "HYPOTHETICAL SENSITIVITY ANALYSIS ONLY: Not a meteorological forecast or prediction. "
                    "Assumes uniform percentage rainfall and delta shifts applied to empirical baseline. "
                    "Soil moisture dynamics are preserved without fabricating unvalidated physical responses. "
                    "Heavy-rain indicator reflects empirical baseline frequency, not recalculated from simulated totals."
                ),
                "unaltered_soil_moisture_notice": (
                    "Soil moisture is held at baseline; empirical satellite observations "
                    "cannot be reliably recalculated from a uniform monthly rainfall shift."
                ),
                "heavy_rain_indicator_note": sim_heavy_rain_note,
            },
            "parameters": {
                "rainfall_pct_change": rainfall_pct_change,
                "temperature_delta_c": temperature_delta_c,
                "dry_spell_delta_days": dry_spell_delta_days,
            },
            "baseline_conditions": {
                "rainfall_mm": base_rain,
                "rainfall_available": rain_available,
                "average_temperature_c": base_temp,
                "temperature_available": temp_available,
                "longest_dry_spell_days": base_dry,
                "dry_spell_available": dry_available,
                "soil_moisture_am": base_sm_am,
            },
            "scenario_conditions": {
                "rainfall_mm": sim_rain,
                "average_temperature_c": sim_temp,
                "longest_dry_spell_days": sim_dry,
                "soil_moisture_am": base_sm_am,
                "soil_moisture_status": "Preserved baseline (not fabricated)",
                "heavy_rain_indicator": sim_heavy_rain_indicator,
            },
            "crop_comparisons": crop_comparisons,
        }
