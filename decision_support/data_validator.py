"""
decision_support.data_validator
Automated data validation across Member 3, Member 4, and core datasets.
Performs file existence, column completeness, type checking, numeric range
validation, null checking on identifiers, and date format validation.
"""
import os
import datetime
from typing import Dict, List, Any, Optional
from .data_loader import DataLoader
from .config import MEMBER_3_DIR, MEMBER_4_DIR


class DataValidator:
    def __init__(self, loader: DataLoader = None):
        self.loader = loader or DataLoader()

    def run_full_validation(self) -> Dict[str, Any]:
        """Runs checks across all datasets and returns a comprehensive validation report."""
        report = {
            "status": "PASSED",
            "datasets_validated": 0,
            "total_checks": 0,
            "passed_checks": 0,
            "warnings": [],
            "errors": [],
            "details": {}
        }

        # 1. Validate Member 4 Agriculture Knowledge Base
        m4_files = {
            "crop_profiles.csv": {
                "required_cols": ["crop_id", "crop_name", "water_requirement_category", "mvp_priority"],
                "non_null_cols": ["crop_id", "crop_name"],
            },
            "crop_calendar.csv": {
                "required_cols": ["crop_id", "region", "season_or_pattern", "sowing_start", "sowing_end"],
                "non_null_cols": ["crop_id", "region"],
            },
            "crop_water_requirements.csv": {
                "required_cols": ["crop_id", "water_requirement_category", "unit", "verification_status"],
                "non_null_cols": ["crop_id", "water_requirement_category"],
            },
            "crop_climate_sensitivity.csv": {
                "required_cols": ["crop_id", "climate_indicator", "qualitative_sensitivity"],
                "non_null_cols": ["crop_id", "climate_indicator"],
            },
            "recommendation_rules.csv": {
                "required_cols": ["rule_id", "trigger_indicator", "farmer_message"],
                "non_null_cols": ["rule_id", "trigger_indicator"],
            },
            "source_register.csv": {
                "required_cols": ["source_id", "publisher_or_dataset", "intended_use"],
                "non_null_cols": ["source_id"],
            }
        }

        for fname, spec in m4_files.items():
            fpath = os.path.join(MEMBER_4_DIR, fname)
            res = self._validate_dataset(
                fpath=fpath,
                fname=f"member_4/{fname}",
                required_cols=spec["required_cols"],
                non_null_cols=spec.get("non_null_cols"),
                numeric_ranges=spec.get("numeric_ranges"),
                date_cols=spec.get("date_cols")
            )
            report["details"][f"member_4/{fname}"] = res
            report["datasets_validated"] += 1
            report["total_checks"] += res["checks_performed"]
            report["passed_checks"] += res["checks_passed"]
            if res["errors"]:
                report["errors"].extend(res["errors"])
            if res["warnings"]:
                report["warnings"].extend(res["warnings"])

        # 2. Validate Member 3 Climate & Risk Observations
        m3_files = {
            "risk_assessment.csv": {
                "required_cols": [
                    "year", "month", "rainfall_mm", "average_temperature_c",
                    "longest_dry_spell_days", "AM_mean", "PM_mean"
                ],
                "non_null_cols": ["year", "month"],
                "numeric_ranges": {
                    "year": (2020, 2025),
                    "month": (1, 12),
                    "rainfall_mm": (0.0, 3000.0),
                    "longest_dry_spell_days": (0, 31)
                }
            },
            "monthly_rainfall.csv": {
                "required_cols": ["year", "month", "rainfall_mm"],
                "non_null_cols": ["year", "month"],
                "numeric_ranges": {
                    "year": (2020, 2025),
                    "month": (1, 12),
                    "rainfall_mm": (0.0, 3000.0)
                }
            },
            "monthly_rainfall_average.csv": {
                "required_cols": ["month", "average_rainfall_mm"],
                "non_null_cols": ["month"],
                "numeric_ranges": {
                    "month": (1, 12),
                    "average_rainfall_mm": (0.0, 1000.0)
                }
            },
            "monthly_temperature.csv": {
                "required_cols": ["month", "average_temperature_c"],
                "non_null_cols": ["month"],
                "numeric_ranges": {
                    "month": (1, 12),
                    "average_temperature_c": (10.0, 50.0)
                }
            },
            "yearly_rainfall.csv": {
                "required_cols": ["year", "annual_rainfall_mm"],
                "non_null_cols": ["year"],
                "numeric_ranges": {
                    "year": (2020, 2025),
                    "annual_rainfall_mm": (0.0, 10000.0)
                }
            },
            "yearly_temperature.csv": {
                "required_cols": ["year", "average_temperature_c"],
                "non_null_cols": ["year"],
                "numeric_ranges": {
                    "year": (2020, 2025),
                    "average_temperature_c": (10.0, 50.0)
                }
            },
            "dry_periods.csv": {
                "required_cols": ["start_date", "end_date", "duration_days"],
                "date_cols": ["start_date", "end_date"],
                "numeric_ranges": {
                    "duration_days": (1, 365)
                }
            },
            "high_rainfall_days.csv": {
                "required_cols": ["date", "PRECTOTCORR"],
                "date_cols": ["date"],
                "numeric_ranges": {
                    "PRECTOTCORR": (0.0, 1000.0)
                }
            },
            "top_rainfall_days.csv": {
                "required_cols": ["date", "PRECTOTCORR"],
                "date_cols": ["date"],
                "numeric_ranges": {
                    "PRECTOTCORR": (0.0, 1000.0)
                }
            },
            "monthly_soil_moisture.csv": {
                "required_cols": ["year", "month", "AM_mean", "PM_mean"],
                "non_null_cols": ["year", "month"],
                "numeric_ranges": {
                    "year": (2020, 2025),
                    "month": (1, 12),
                    "AM_mean": (0.0, 1.0),
                    "PM_mean": (0.0, 1.0)
                }
            },
            "average_monthly_soil_moisture.csv": {
                "required_cols": ["month", "AM_mean", "PM_mean"],
                "non_null_cols": ["month"],
                "numeric_ranges": {
                    "month": (1, 12),
                    "AM_mean": (0.0, 1.0),
                    "PM_mean": (0.0, 1.0)
                }
            },
            "rainfall_soilmoisture_comparison.csv": {
                "required_cols": ["year", "month", "rainfall_mm", "AM_mean", "PM_mean"],
                "non_null_cols": ["year", "month"],
                "numeric_ranges": {
                    "year": (2020, 2025),
                    "month": (1, 12),
                    "rainfall_mm": (0.0, 3000.0)
                }
            }
        }

        for fname, spec in m3_files.items():
            fpath = os.path.join(MEMBER_3_DIR, fname)
            res = self._validate_dataset(
                fpath=fpath,
                fname=f"member_3/{fname}",
                required_cols=spec["required_cols"],
                non_null_cols=spec.get("non_null_cols"),
                numeric_ranges=spec.get("numeric_ranges"),
                date_cols=spec.get("date_cols")
            )
            report["details"][f"member_3/{fname}"] = res
            report["datasets_validated"] += 1
            report["total_checks"] += res["checks_performed"]
            report["passed_checks"] += res["checks_passed"]
            if res["errors"]:
                report["errors"].extend(res["errors"])
            if res["warnings"]:
                report["warnings"].extend(res["warnings"])

        # 3. Check six crops integrity
        crops_res = self._validate_crops_catalog()
        report["details"]["crops_integrity"] = crops_res
        report["total_checks"] += crops_res["checks_performed"]
        report["passed_checks"] += crops_res["checks_passed"]
        if crops_res["errors"]:
            report["errors"].extend(crops_res["errors"])
        if crops_res["warnings"]:
            report["warnings"].extend(crops_res["warnings"])

        # Final overall status
        if report["errors"]:
            report["status"] = "FAILED"
        elif report["warnings"]:
            report["status"] = "PASSED_WITH_WARNINGS"

        return report

    def _validate_dataset(
        self,
        fpath: str,
        fname: str,
        required_cols: List[str],
        non_null_cols: Optional[List[str]] = None,
        numeric_ranges: Optional[Dict[str, tuple]] = None,
        date_cols: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Validates file existence, non-emptiness, required columns, non-null values, ranges and dates."""
        non_null_cols = non_null_cols or []
        numeric_ranges = numeric_ranges or {}
        date_cols = date_cols or []

        res = {
            "file": fname,
            "exists": os.path.exists(fpath),
            "rows": 0,
            "columns": [],
            "missing_required_cols": [],
            "checks_performed": 2 + len(required_cols) + len(non_null_cols) + len(numeric_ranges) + len(date_cols),
            "checks_passed": 0,
            "warnings": [],
            "errors": []
        }

        # 1. Existence check
        if not res["exists"]:
            res["errors"].append(f"Required dataset '{fname}' is missing from filesystem.")
            return res
        res["checks_passed"] += 1

        # 2. Non-empty check
        rows = self.loader._read_csv(fpath)
        res["rows"] = len(rows)
        if len(rows) == 0:
            res["warnings"].append(f"Dataset '{fname}' exists but has 0 records.")
            return res
        res["checks_passed"] += 1

        res["columns"] = list(rows[0].keys())

        # 3. Column existence checks
        for req in required_cols:
            if req not in res["columns"]:
                res["missing_required_cols"].append(req)
                res["errors"].append(f"Missing required column '{req}' in '{fname}'")
            else:
                res["checks_passed"] += 1

        # 4. Non-null identifier checks
        for col in non_null_cols:
            if col in res["columns"]:
                has_null = any(r.get(col) is None or str(r.get(col)).strip() == "" for r in rows)
                if has_null:
                    res["errors"].append(f"Column '{col}' in '{fname}' contains null/empty values.")
                else:
                    res["checks_passed"] += 1
            else:
                res["errors"].append(f"Cannot perform non-null check: column '{col}' missing in '{fname}'")

        # 5. Numeric range validation checks
        for col, (min_v, max_v) in numeric_ranges.items():
            if col in res["columns"]:
                out_of_range = False
                for r in rows:
                    val = r.get(col)
                    if val is not None and str(val).strip() not in ("", "-9999", "None"):
                        try:
                            fval = float(val)
                            if not (min_v <= fval <= max_v):
                                out_of_range = True
                                res["errors"].append(
                                    f"Value {fval} in '{col}' exceeds valid range [{min_v}, {max_v}] in '{fname}'"
                                )
                                break
                        except ValueError:
                            out_of_range = True
                            res["errors"].append(f"Non-numeric value '{val}' in numeric column '{col}' in '{fname}'")
                            break
                if not out_of_range:
                    res["checks_passed"] += 1
            else:
                res["errors"].append(f"Cannot perform range check: column '{col}' missing in '{fname}'")

        # 6. Date format validation checks
        for col in date_cols:
            if col in res["columns"]:
                bad_date = False
                for r in rows:
                    val = r.get(col)
                    if val:
                        try:
                            datetime.date.fromisoformat(str(val).strip())
                        except ValueError:
                            bad_date = True
                            res["errors"].append(f"Invalid date format '{val}' in '{col}' in '{fname}' (expected YYYY-MM-DD)")
                            break
                if not bad_date:
                    res["checks_passed"] += 1
            else:
                res["errors"].append(f"Cannot perform date check: column '{col}' missing in '{fname}'")

        return res

    def _validate_crops_catalog(self) -> Dict[str, Any]:
        """Validates all 6 mandated crops are present and non-empty in crop profiles."""
        expected_crops = {"rice", "groundnut", "banana", "coconut", "tapioca", "sugarcane"}
        profiles = self.loader.load_crop_profiles()
        found_crops = {r.get("crop_id") for r in profiles if r.get("crop_id")}

        res = {
            "expected_crops": list(expected_crops),
            "found_crops": list(found_crops),
            "checks_performed": 6,
            "checks_passed": 0,
            "warnings": [],
            "errors": []
        }

        for c in expected_crops:
            if c in found_crops:
                res["checks_passed"] += 1
            else:
                res["errors"].append(f"Mandated crop '{c}' is missing from crop_profiles.csv")

        return res
