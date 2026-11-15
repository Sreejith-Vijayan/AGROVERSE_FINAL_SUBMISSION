"""
decision_support.crop_suitability
Six-crop suitability evaluation engine for Palakkad Agro-Ecological Units.
Uses verified Member 4 agricultural KB and empirical Member 3 & NASA climate observations.
"""
from typing import Dict, List, Any, Optional
from .data_loader import DataLoader
from .climate_analyzer import ClimateAnalyzer
from .explanation_engine import ExplanationEngine
from .schemas import CropSuitabilityResult

MONTH_NAMES = ["January", "February", "March", "April", "May", "June",
               "July", "August", "September", "October", "November", "December"]


class CropSuitabilityEngine:
    def __init__(self, loader: DataLoader = None, analyzer: ClimateAnalyzer = None):
        self.loader = loader or DataLoader()
        self.analyzer = analyzer or ClimateAnalyzer(self.loader)
        self._load_knowledge_base()

    def _load_knowledge_base(self):
        self.profiles = {r["crop_id"]: r for r in self.loader.load_crop_profiles() if r.get("crop_id")}
        self.calendars = self.loader.load_crop_calendar()
        self.water_reqs = {r["crop_id"]: r for r in self.loader.load_crop_water_requirements() if r.get("crop_id")}
        self.sensitivities = self.loader.load_crop_climate_sensitivity()
        self.rules = self.loader.load_recommendation_rules()

    def evaluate_all_crops(
        self,
        target_month: int = 5,
        climate_override: Optional[Dict[str, Any]] = None
    ) -> List[CropSuitabilityResult]:
        """Evaluates all 6 crops for a given month/period or modified climate scenario."""
        results = []
        ordered_crops = ["rice", "groundnut", "banana", "coconut", "tapioca", "sugarcane"]
        for crop_id in ordered_crops:
            res = self.evaluate_crop(crop_id, target_month=target_month, climate_override=climate_override)
            results.append(res)
        return results

    def evaluate_crop(
        self,
        crop_id: str,
        target_month: int = 5,
        climate_override: Optional[Dict[str, Any]] = None
    ) -> CropSuitabilityResult:
        profile = self.profiles.get(crop_id, {})
        crop_name = profile.get("crop_name", crop_id.title())
        priority = profile.get("mvp_priority", "Core")
        month_name = MONTH_NAMES[target_month - 1]
        period_label = f"Month: {month_name} (Seasonal context)"

        # ----------------------------------------------------------------
        # 1. Fetch climate metrics (baseline or overridden)
        # ----------------------------------------------------------------
        if climate_override:
            rainfall = climate_override.get("rainfall_mm")
            temp = climate_override.get("average_temperature_c")
            dry_spell_days = climate_override.get("longest_dry_spell_days")
            dry_spell_7plus = (dry_spell_days >= 7) if dry_spell_days is not None else False
            heavy_rain = climate_override.get("heavy_rain_month_indicator", False)
            soil_moist_am = climate_override.get("AM_mean")
            period_label += " [Scenario Modified]"
        else:
            monthly_summary = self.analyzer.get_monthly_climate_summary(target_month=target_month)[0]
            risk_summary = self.analyzer.get_risk_indicators_summary(month=target_month)
            rainfall = monthly_summary.get("average_rainfall_mm")
            temp = monthly_summary.get("average_temperature_c")
            dry_spell_days = risk_summary.get("avg_longest_dry_spell_days")
            dry_spell_7plus = risk_summary.get("dry_spell_7plus_frequency_pct", 0) > 40
            heavy_rain = risk_summary.get("heavy_rain_months_frequency_pct", 0) > 30
            soil_moist_am = monthly_summary.get("soil_moisture_am")

        # ----------------------------------------------------------------
        # 2. Extract agronomic parameters
        # ----------------------------------------------------------------
        crop_calendars = [c for c in self.calendars if c.get("crop_id") == crop_id]
        crop_water = self.water_reqs.get(crop_id, {})
        crop_sens = [s for s in self.sensitivities if s.get("crop_id") == crop_id]

        # ----------------------------------------------------------------
        # 3. Check calendar alignment
        # Correctly handles: inclusive ranges, year-boundary ranges,
        # perennial crops, and distinguishes sowing/planting/harvest windows.
        # ----------------------------------------------------------------
        is_sowing_window = False
        is_planting_window = False   # used for perennial crops' planting window
        is_harvest_window = False
        is_active_growth = False
        active_seasons = []

        month_order = {name: i + 1 for i, name in enumerate(MONTH_NAMES)}

        def months_between(start, end):
            """Return inclusive list of month names, handling year-boundary wrap-around."""
            if not start or not end:
                return []
            if start not in month_order or end not in month_order:
                return []
            start_num = month_order[start]
            end_num = month_order[end]
            if start_num <= end_num:
                return [MONTH_NAMES[i - 1] for i in range(start_num, end_num + 1)]
            # Year-boundary (e.g. September -> January)
            return (
                [MONTH_NAMES[i - 1] for i in range(start_num, 13)]
                + [MONTH_NAMES[i - 1] for i in range(1, end_num + 1)]
            )

        for cal in crop_calendars:
            s_start = cal.get("sowing_start")
            s_end = cal.get("sowing_end")
            h_start = cal.get("harvest_start")
            h_end = cal.get("harvest_end")
            pattern = cal.get("season_or_pattern", "Main")

            # Detect perennial pattern: keyword in pattern OR harvest is year-round
            is_perennial = (
                "perennial" in str(pattern).lower()
                or str(h_start).strip().lower() == "year-round"
                or str(h_end).strip().lower() == "year-round"
            )

            if is_perennial:
                # Perennial crops (e.g. coconut) are always actively growing
                is_active_growth = True
                # Check whether target month falls within the documented planting window
                planting_months = months_between(s_start, s_end)
                if month_name in planting_months:
                    is_planting_window = True
                    active_seasons.append(f"{pattern} (Planting window)")
                else:
                    active_seasons.append(f"{pattern} (Perennial — actively growing year-round)")
            else:
                sowing_months = months_between(s_start, s_end)
                harvest_months = months_between(h_start, h_end)

                # Sowing window check
                if month_name in sowing_months:
                    is_sowing_window = True
                    active_seasons.append(f"{pattern} (Sowing)")

                # Harvest window check
                if month_name in harvest_months:
                    is_harvest_window = True
                    active_seasons.append(f"{pattern} (Harvest)")

                # Active crop-cycle check: only if month falls between sowing start
                # and harvest end (inclusive), accounting for year-boundary crops.
                # We do NOT assume every crop is growing just because it has a calendar entry.
                if sowing_months and harvest_months:
                    cycle_months = months_between(s_start, h_end)
                    if month_name in cycle_months:
                        is_active_growth = True
                        if month_name not in sowing_months and month_name not in harvest_months:
                            active_seasons.append(f"{pattern} (Within crop cycle)")

        # ----------------------------------------------------------------
        # 4. Synthesize supporting factors, risk factors, and monitoring notes
        # ----------------------------------------------------------------
        supporting_factors = []
        risk_factors = []
        monitoring_considerations = []
        missing_information = [
            "Farm-level irrigation infrastructure & canal schedule status",
            "Field drainage condition and soil compaction depth",
            "Field-specific soil moisture capacitance probe measurements",
            "Variety-specific thermal heat degree day tolerance"
        ]

        # --- Calendar alignment messages ---
        if is_sowing_window:
            supporting_factors.append(
                f"{month_name} matches a documented sowing window: "
                f"{', '.join(active_seasons)}."
            )
        if is_planting_window:
            supporting_factors.append(
                f"{month_name} falls within the documented planting window for "
                f"this perennial crop: {', '.join(active_seasons)}."
            )
        if is_harvest_window:
            supporting_factors.append(
                f"{month_name} matches a documented harvest window: "
                f"{', '.join(active_seasons)}."
            )
        if is_active_growth and not is_sowing_window and not is_harvest_window and not is_planting_window:
            supporting_factors.append(
                f"{month_name} falls within the documented crop cycle "
                f"({', '.join(active_seasons)}). "
                "Exact growth stage is not available from the knowledge base."
            )
        if not is_sowing_window and not is_harvest_window and not is_active_growth and not is_planting_window:
            supporting_factors.append(
                f"No documented sowing, planting, harvest, or active crop-cycle "
                f"window is recorded for {month_name} in the knowledge base."
            )

        # --- Water requirement: preserve M4 info; never compare with one month's rainfall ---
        # Monthly rainfall is NOT directly comparable to crop-cycle water requirement.
        # We note observed rainfall as descriptive climate context only.
        if rainfall is not None:
            monitoring_considerations.append(
                f"Observed monthly rainfall for {month_name}: {rainfall:.1f} mm. "
                "This is a single-month total and is not directly comparable to the "
                "crop-cycle water requirement (which spans the entire growing season). "
                "Actual water balance requires crop-cycle irrigation scheduling and "
                "effective rainfall estimation across the season."
            )
        else:
            missing_information.append(
                f"Observed monthly rainfall data is unavailable for {month_name}."
            )

        # --- Dry-spell sensitivity: use only documented values; unknown ≠ moderate ---
        sens_map = {
            s.get("climate_indicator"): s.get("qualitative_sensitivity", "unknown")
            for s in crop_sens
        }

        dry_sens = sens_map.get("prolonged_dry_spell", "unknown")
        dry_str = f"{dry_spell_days:.0f} days" if dry_spell_days is not None else "extended periods"
        if dry_spell_7plus:
            if dry_sens == "high":
                risk_factors.append(
                    f"Potential dry-spell concern: the observed average longest dry "
                    f"period for {month_name} is {dry_str}. "
                    "The crop is documented as highly sensitive to prolonged dry spells."
                )
                monitoring_considerations.append(
                    "Check soil moisture and irrigation availability during prolonged "
                    "rain-free periods."
                )
            elif dry_sens in ("moderate", "moderate_to_high"):
                risk_factors.append(
                    f"Potential moisture stress: dry periods were observed in {month_name} "
                    f"(average longest dry period: {dry_str}). "
                    "The crop shows moderate sensitivity to prolonged dry spells."
                )
            elif dry_sens == "unknown":
                monitoring_considerations.append(
                    f"Dry periods were observed in {month_name} "
                    f"(avg longest: {dry_str}), but crop-specific sensitivity "
                    "to prolonged dry spells is not established in the knowledge base."
                )

        # --- Excess rainfall sensitivity ---
        excess_sens = sens_map.get("excess_rainfall", "unknown")
        if heavy_rain:
            if excess_sens == "high":
                risk_factors.append(
                    f"Potential excess-rainfall or waterlogging concern in {month_name}. "
                    "Rainfall observations alone do not confirm field flooding; "
                    "field drainage must be assessed."
                )
                monitoring_considerations.append(
                    "Inspect field drainage and avoid planting in saturated seedbeds."
                )
            elif excess_sens in ("moderate", "moderate_to_high"):
                risk_factors.append(
                    f"Potential drainage concern during periods of elevated "
                    f"heavy-rainfall frequency in {month_name}."
                )
            elif excess_sens == "unknown":
                monitoring_considerations.append(
                    f"Elevated heavy-rainfall frequency was observed in {month_name}, "
                    "but crop-specific excess-rainfall sensitivity is not established "
                    "in the knowledge base."
                )

        # --- Temperature: descriptive context only; no suitability claim without thresholds ---
        temp_sens = sens_map.get("high_temperature", "unknown")
        if temp is not None:
            monitoring_considerations.append(
                f"Observed monthly mean temperature for {month_name}: {temp:.1f}°C. "
                "Crop- and growth-stage-specific heat stress thresholds are not "
                "available in this knowledge base, so no temperature suitability "
                "claim is made."
            )
        else:
            missing_information.append(
                f"Observed monthly mean temperature data is unavailable for {month_name}."
            )
        if temp_sens == "unknown":
            monitoring_considerations.append(
                "High-temperature sensitivity for this crop is not established "
                "in the knowledge base. Temperature observations are reported as "
                "descriptive climate context only."
            )

        # --- SMAP: regional satellite context; not field-level adequacy ---
        # -9999 and empty values are already filtered to None by DataLoader.
        if soil_moist_am is not None:
            supporting_factors.append(
                f"Regional satellite soil-moisture observation (SMAP, ~36 km grid): "
                f"{soil_moist_am:.3f} cm³/cm³. "
                "This is a landscape-level satellite measurement and does not "
                "establish field-level crop water availability."
            )
        else:
            missing_information.append(
                "No valid regional satellite soil-moisture observation (SMAP) "
                "is available for this assessment period."
            )

        # ----------------------------------------------------------------
        # 5. Determine suitability status
        # ----------------------------------------------------------------
        if not crop_water or not crop_calendars:
            suitability_status = "Insufficient data for assessment"
        elif len(risk_factors) >= 3:
            suitability_status = "Potentially unsuitable under observed conditions"
        elif len(risk_factors) >= 1:
            suitability_status = "Needs careful evaluation"
        elif not is_sowing_window and not is_active_growth and not is_planting_window:
            # No calendar activity — but do NOT penalise perennial crops
            suitability_status = "Needs careful evaluation"
        else:
            suitability_status = "Suitable for further consideration"

        # ----------------------------------------------------------------
        # 6. Build water requirement info dict
        # Preserve M4 data exactly; never compare directly with monthly rainfall.
        # ----------------------------------------------------------------
        water_requirement_info = {}
        if crop_water:
            water_requirement_info = {
                "category": crop_water.get("water_requirement_category", "N/A"),
                "value": crop_water.get("crop_water_requirement_value", "N/A"),
                "unit": crop_water.get("unit", "N/A"),
                "interpretation": crop_water.get("interpretation", "N/A"),
                "source": crop_water.get("source_to_verify", "N/A"),
                "verification_status": crop_water.get("verification_status", "unverified"),
                "comparability_note": (
                    "Crop-cycle water requirement and single-month rainfall are not "
                    "directly comparable. The published requirement spans the full crop "
                    "cycle; monthly rainfall is a one-month total. Actual water balance "
                    "requires irrigation scheduling and effective rainfall estimation."
                )
            }
            # Coconut has litres/palm/irrigation — explicitly flag incompatibility with mm
            if crop_id == "coconut":
                water_requirement_info["unit_context"] = (
                    "Coconut water requirement is expressed in litres per palm per "
                    "irrigation event, not in mm. Direct comparison with rainfall "
                    "measured in mm is not valid."
                )

        # ----------------------------------------------------------------
        # 7. Climate sensitivity info (preserve M4 data)
        # ----------------------------------------------------------------
        climate_sensitivity_info = []
        for s in crop_sens:
            sens_val = s.get("qualitative_sensitivity", "unknown")
            entry = {
                "climate_indicator": s.get("climate_indicator"),
                "qualitative_sensitivity": sens_val,
                "interpretation": s.get("interpretation", ""),
            }
            if sens_val == "unknown":
                entry["unknown_note"] = (
                    "Crop-specific sensitivity for this indicator is not established "
                    "in the knowledge base. It must not be treated as moderate or any "
                    "other assumed level."
                )
            climate_sensitivity_info.append(entry)

        # ----------------------------------------------------------------
        # 8. Crop calendar info (preserve M4 data)
        # ----------------------------------------------------------------
        crop_calendar_info = []
        for cal in crop_calendars:
            crop_calendar_info.append({
                "region": cal.get("region"),
                "season_or_pattern": cal.get("season_or_pattern"),
                "sowing_start": cal.get("sowing_start"),
                "sowing_end": cal.get("sowing_end"),
                "harvest_start": cal.get("harvest_start"),
                "harvest_end": cal.get("harvest_end"),
                "source": cal.get("source_to_verify"),
                "verification_status": cal.get("verification_status", "unverified")
            })

        # ----------------------------------------------------------------
        # 9. Verification status — derived from M4 data; never default to "verified"
        # ----------------------------------------------------------------
        water_verif = crop_water.get("verification_status", "") if crop_water else ""
        if water_verif in ("verified", "verified_numerical"):
            verification_status = water_verif
        else:
            cal_verifs = [c.get("verification_status", "") for c in crop_calendars]
            if "verified" in cal_verifs:
                verification_status = "verified"
            else:
                verification_status = "not_assessed"

        # ----------------------------------------------------------------
        # 10. Comparative score — transparent, deterministic index (0-100)
        # This is an EXPLORATORY SOFTWARE INDEX, not yield prediction or guaranteed
        # agronomic suitability. Scoring logic is documented here.
        #
        # Components:
        #   Calendar alignment:  40 pts (sowing/planting), 30 pts (harvest),
        #                        20 pts (within cycle), 5 pts (outside cycle)
        #   Risk penalty:        -15 pts per documented risk factor (floored at 0)
        #   Data completeness:   up to 20 pts (water req + calendar + sensitivity)
        # ----------------------------------------------------------------
        score = 0.0

        if is_sowing_window or is_planting_window:
            score += 40.0
        elif is_harvest_window:
            score += 30.0
        elif is_active_growth:
            score += 20.0
        else:
            score += 5.0

        # Risk penalty
        risk_penalty = min(len(risk_factors) * 15.0, score)
        score = max(0.0, score - risk_penalty)

        # Data completeness bonus (up to 20 pts)
        if crop_water:
            score += 7.0
        if crop_calendars:
            score += 7.0
        if crop_sens:
            score += 6.0

        comparative_score = round(max(0.0, min(100.0, score)), 1)

        # ----------------------------------------------------------------
        # 11. Evidence coverage — None; no defensible documented method exists
        # to calculate a single percentage from these heterogeneous sources.
        # ----------------------------------------------------------------
        evidence_coverage_pct = None

        # ----------------------------------------------------------------
        # 12. Uncertainty level — conservative; based on actual data completeness
        # ----------------------------------------------------------------
        missing_critical = len(missing_information)
        if suitability_status == "Insufficient data for assessment":
            uncertainty_level = "High"
        elif missing_critical >= 4:
            uncertainty_level = "Moderate-to-High"
        else:
            uncertainty_level = "Moderate"

        # ----------------------------------------------------------------
        # 13. Add water requirement note to missing_information
        # ----------------------------------------------------------------
        if crop_water:
            missing_information.append(
                "Actual crop-cycle water balance, effective rainfall, and "
                "farm-level irrigation availability are not established."
            )

        # ----------------------------------------------------------------
        # 14. Generate natural-language explanation
        # ----------------------------------------------------------------
        explanation = ExplanationEngine.generate_explanation(
            crop_name=crop_name,
            suitability_status=suitability_status,
            supporting_factors=supporting_factors,
            risk_factors=risk_factors,
            missing_information=missing_information
        )

        # ----------------------------------------------------------------
        # 15. Return the complete, fully-populated result object
        # ----------------------------------------------------------------
        return CropSuitabilityResult(
            crop_id=crop_id,
            crop_name=crop_name,
            priority=priority,
            suitability_status=suitability_status,
            assessment_period=period_label,
            supporting_factors=supporting_factors,
            risk_factors=risk_factors,
            water_requirement_info=water_requirement_info,
            climate_sensitivity_info=climate_sensitivity_info,
            crop_calendar_info=crop_calendar_info,
            missing_information=missing_information,
            verification_status=verification_status,
            explanation=explanation,
            monitoring_considerations=monitoring_considerations,
            comparative_score=comparative_score,
            evidence_coverage_pct=evidence_coverage_pct,
            uncertainty_level=uncertainty_level
        )
