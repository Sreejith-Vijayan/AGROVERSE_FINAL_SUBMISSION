"""
decision_support.data_loader
Centralized data loader for Member 3, Member 4, and 07_UI_HANDOVER datasets.
Preserves null values, formats, and handles spatial metadata correctly.
"""
import os
import csv
import json
from typing import Dict, List, Any, Optional
from .config import (
    MEMBER_3_DIR,
    MEMBER_4_DIR,
    HANDOVER_CSV_DIR,
    HANDOVER_JSON_DIR,
    LOCATIONS,
    SOURCE_REGISTRY_METADATA
)

class DataLoader:
    def __init__(self):
        self._cache = {}

    def _read_csv(self, file_path: str) -> List[Dict[str, Any]]:
        if not os.path.exists(file_path):
            return []
        rows = []
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Clean keys and preserve None/null for empty strings
                cleaned_row = {}
                for k, v in row.items():
                    if k is None:
                        continue
                    key = k.strip()
                    val = v.strip() if v is not None else ""
                    # Handle SMAP invalid value flag -9999 or empty
                    if val == "" or val == "-9999" or val == "-9999.0":
                        cleaned_row[key] = None
                    else:
                        cleaned_row[key] = val
                rows.append(cleaned_row)
        return rows

    def _read_json(self, file_path: str) -> Dict[str, Any]:
        if not os.path.exists(file_path):
            return {"meta": {}, "data": []}
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    # ---------------- Member 4 Data Ingestion ----------------
    def load_crop_profiles(self) -> List[Dict[str, Any]]:
        return self._read_csv(os.path.join(MEMBER_4_DIR, "crop_profiles.csv"))

    def load_crop_calendar(self) -> List[Dict[str, Any]]:
        return self._read_csv(os.path.join(MEMBER_4_DIR, "crop_calendar.csv"))

    def load_crop_water_requirements(self) -> List[Dict[str, Any]]:
        return self._read_csv(os.path.join(MEMBER_4_DIR, "crop_water_requirements.csv"))

    def load_crop_climate_sensitivity(self) -> List[Dict[str, Any]]:
        return self._read_csv(os.path.join(MEMBER_4_DIR, "crop_climate_sensitivity.csv"))

    def load_recommendation_rules(self) -> List[Dict[str, Any]]:
        return self._read_csv(os.path.join(MEMBER_4_DIR, "recommendation_rules.csv"))

    def load_source_register(self) -> List[Dict[str, Any]]:
        return self._read_csv(os.path.join(MEMBER_4_DIR, "source_register.csv"))

    # ---------------- Member 3 Data Ingestion ----------------
    def load_risk_assessment(self) -> List[Dict[str, Any]]:
        return self._read_csv(os.path.join(MEMBER_3_DIR, "risk_assessment.csv"))

    def load_monthly_rainfall(self) -> List[Dict[str, Any]]:
        return self._read_csv(os.path.join(MEMBER_3_DIR, "monthly_rainfall.csv"))

    def load_monthly_rainfall_average(self) -> List[Dict[str, Any]]:
        return self._read_csv(os.path.join(MEMBER_3_DIR, "monthly_rainfall_average.csv"))

    def load_yearly_rainfall(self) -> List[Dict[str, Any]]:
        return self._read_csv(os.path.join(MEMBER_3_DIR, "yearly_rainfall.csv"))

    def load_monthly_temperature(self) -> List[Dict[str, Any]]:
        return self._read_csv(os.path.join(MEMBER_3_DIR, "monthly_temperature.csv"))

    def load_yearly_temperature(self) -> List[Dict[str, Any]]:
        return self._read_csv(os.path.join(MEMBER_3_DIR, "yearly_temperature.csv"))

    def load_dry_periods(self) -> List[Dict[str, Any]]:
        return self._read_csv(os.path.join(MEMBER_3_DIR, "dry_periods.csv"))

    def load_high_rainfall_days(self) -> List[Dict[str, Any]]:
        return self._read_csv(os.path.join(MEMBER_3_DIR, "high_rainfall_days.csv"))

    def load_top_rainfall_days(self) -> List[Dict[str, Any]]:
        return self._read_csv(os.path.join(MEMBER_3_DIR, "top_rainfall_days.csv"))

    def load_monthly_soil_moisture(self) -> List[Dict[str, Any]]:
        return self._read_csv(os.path.join(MEMBER_3_DIR, "monthly_soil_moisture.csv"))

    def load_average_monthly_soil_moisture(self) -> List[Dict[str, Any]]:
        return self._read_csv(os.path.join(MEMBER_3_DIR, "average_monthly_soil_moisture.csv"))

    def load_rainfall_soilmoisture_comparison(self) -> List[Dict[str, Any]]:
        return self._read_csv(os.path.join(MEMBER_3_DIR, "rainfall_soilmoisture_comparison.csv"))

    # ---------------- Existing 07_UI_HANDOVER Ingestion ----------------
    def load_handover_monthly_climate_smap(self) -> Dict[str, Any]:
        return self._read_json(os.path.join(HANDOVER_JSON_DIR, "monthly_climate_smap.json"))

    def load_handover_soil_properties(self) -> Dict[str, Any]:
        return self._read_json(os.path.join(HANDOVER_JSON_DIR, "static_soil_properties.json"))

    def load_handover_yearly_summary(self) -> Dict[str, Any]:
        return self._read_json(os.path.join(HANDOVER_JSON_DIR, "yearly_climate_summary.json"))

    def load_handover_seasonal_summary(self) -> Dict[str, Any]:
        return self._read_json(os.path.join(HANDOVER_JSON_DIR, "seasonal_climate_summary.json"))

    # ---------------- Metadata & Source Registry ----------------
    def get_source_registry(self) -> List[Dict[str, Any]]:
        return SOURCE_REGISTRY_METADATA

    def get_spatial_locations(self) -> Dict[str, Any]:
        return LOCATIONS
