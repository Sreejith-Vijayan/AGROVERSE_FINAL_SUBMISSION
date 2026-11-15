"""
decision_support.climate_analyzer
Aggregates and analyzes empirical climate data from Member 3 datasets
and baseline NASA POWER / SMAP observations for Palakkad.
"""
from typing import Dict, List, Any, Optional
from .data_loader import DataLoader

class ClimateAnalyzer:
    def __init__(self, loader: DataLoader = None):
        self.loader = loader or DataLoader()

    def get_monthly_climate_summary(self, target_month: Optional[int] = None) -> List[Dict[str, Any]]:
        """Returns monthly rainfall, temperature and soil moisture statistics across 2020-2025."""
        rain_avg = {int(r["month"]): float(r["average_rainfall_mm"]) for r in self.loader.load_monthly_rainfall_average() if r.get("month")}
        temp_avg = {int(r["month"]): float(r["average_temperature_c"]) for r in self.loader.load_monthly_temperature() if r.get("month")}
        sm_avg = {int(r["month"]): {
            "AM_mean": float(r["AM_mean"]) if r.get("AM_mean") else None,
            "PM_mean": float(r["PM_mean"]) if r.get("PM_mean") else None
        } for r in self.loader.load_average_monthly_soil_moisture() if r.get("month")}

        summaries = []
        months = [target_month] if target_month else list(range(1, 13))
        month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

        for m in months:
            summaries.append({
                "month": m,
                "month_name": month_names[m - 1],
                "average_rainfall_mm": rain_avg.get(m),
                "average_temperature_c": temp_avg.get(m),
                "soil_moisture_am": sm_avg.get(m, {}).get("AM_mean"),
                "soil_moisture_pm": sm_avg.get(m, {}).get("PM_mean"),
                "units": {
                    "rainfall": "mm/month",
                    "temperature": "°C",
                    "soil_moisture": "cm³/cm³ (m³/m³ volumetric)"
                }
            })
        return summaries

    def get_risk_indicators_summary(self, month: Optional[int] = None) -> Dict[str, Any]:
        """Summarizes risk indicators from Member 3 risk_assessment.csv."""
        records = self.loader.load_risk_assessment()
        if month:
            records = [r for r in records if int(r.get("month", 0)) == month]

        if not records:
            return {
                "records_count": 0,
                "avg_rainfall_mm": None,
                "avg_temp_c": None,
                "max_dry_spell_days": None,
                "dry_spell_7plus_frequency_pct": 0,
                "heavy_rain_months_frequency_pct": 0,
                "low_soil_moisture_am_pct": 0
            }

        total = len(records)
        rain_vals = [float(r["rainfall_mm"]) for r in records if r.get("rainfall_mm") is not None]
        temp_vals = [float(r["average_temperature_c"]) for r in records if r.get("average_temperature_c") is not None]
        dry_spells = [int(r["longest_dry_spell_days"]) for r in records if r.get("longest_dry_spell_days") is not None]

        dry_7plus_count = sum(1 for r in records if str(r.get("dry_spell_7plus_days")).lower() == "true")
        heavy_rain_count = sum(1 for r in records if str(r.get("heavy_rain_month_indicator")).lower() == "true")
        am_low_count = sum(1 for r in records if str(r.get("AM_low_soil_moisture_relative")).lower() == "true")

        return {
            "records_count": total,
            "avg_rainfall_mm": round(sum(rain_vals) / len(rain_vals), 2) if rain_vals else None,
            "avg_temp_c": round(sum(temp_vals) / len(temp_vals), 2) if temp_vals else None,
            "max_dry_spell_days": max(dry_spells) if dry_spells else None,
            "avg_longest_dry_spell_days": round(sum(dry_spells) / len(dry_spells), 1) if dry_spells else None,
            "dry_spell_7plus_frequency_pct": round((dry_7plus_count / total) * 100, 1) if total else 0,
            "heavy_rain_months_frequency_pct": round((heavy_rain_count / total) * 100, 1) if total else 0,
            "low_soil_moisture_am_pct": round((am_low_count / total) * 100, 1) if total else 0
        }
