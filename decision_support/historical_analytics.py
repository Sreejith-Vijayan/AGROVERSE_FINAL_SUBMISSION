"""
decision_support.historical_analytics
Historical analytical data structures integrating Member 3 datasets:
Rainfall, temperature, dry spells, extreme rainfall days, and soil moisture comparisons.
"""
from typing import Dict, List, Any
from .data_loader import DataLoader

class HistoricalAnalytics:
    def __init__(self, loader: DataLoader = None):
        self.loader = loader or DataLoader()

    def get_full_climate_history(self) -> Dict[str, Any]:
        """Provides verified 2020-2025 time-series and event registries."""
        return {
            "meta": {
                "coverage": "2020 - 2025 (Verified)",
                "location": "Palakkad, Kerala",
                "sources": "Member 3 Handover & NASA POWER"
            },
            "yearly_rainfall": self.loader.load_yearly_rainfall(),
            "monthly_rainfall": self.loader.load_monthly_rainfall(),
            "monthly_rainfall_average": self.loader.load_monthly_rainfall_average(),
            "yearly_temperature": self.loader.load_yearly_temperature(),
            "monthly_temperature": self.loader.load_monthly_temperature(),
            "dry_periods": self.loader.load_dry_periods(),
            "high_rainfall_days": self.loader.load_high_rainfall_days(),
            "top_rainfall_days": self.loader.load_top_rainfall_days(),
            "monthly_soil_moisture": self.loader.load_monthly_soil_moisture(),
            "average_monthly_soil_moisture": self.loader.load_average_monthly_soil_moisture(),
            "rainfall_soilmoisture_comparison": self.loader.load_rainfall_soilmoisture_comparison()
        }

    def get_integrated_risk_assessment(self) -> Dict[str, Any]:
        """Returns risk assessment table with thresholds and indicators."""
        records = self.loader.load_risk_assessment()
        return {
            "meta": {
                "source": "Member 3 risk_assessment.csv",
                "coverage": "2020-01 to 2025-12",
                "records": len(records),
                "thresholds": {
                    "heavy_rain_daily_threshold_mm": 16.3525,
                    "am_low_moisture_q25_threshold": 0.248,
                    "pm_low_moisture_q25_threshold": 0.239,
                    "dry_spell_risk_days": 7
                }
            },
            "data": records
        }
