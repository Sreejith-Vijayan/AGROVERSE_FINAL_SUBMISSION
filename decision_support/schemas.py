"""
decision_support.schemas
Schemas and data classes for Decision Support and What-If Simulator.
"""
from typing import Dict, List, Any, Optional

class DataValidationError(Exception):
    """Raised when critical dataset validation fails."""
    pass

class CropSuitabilityResult:
    def __init__(
        self,
        crop_id: str,
        crop_name: str,
        priority: str,
        suitability_status: str,
        assessment_period: str,
        supporting_factors: List[str],
        risk_factors: List[str],
        water_requirement_info: Dict[str, Any],
        climate_sensitivity_info: List[Dict[str, Any]],
        crop_calendar_info: List[Dict[str, Any]],
        missing_information: List[str],
        verification_status: str,
        explanation: str,
        monitoring_considerations: List[str],
        comparative_score: Optional[float] = None,
        evidence_coverage_pct: Optional[float] = None,
        uncertainty_level: Optional[str] = "Moderate"
    ):
        self.crop_id = crop_id
        self.crop_name = crop_name
        self.priority = priority
        self.suitability_status = suitability_status
        self.assessment_period = assessment_period
        self.supporting_factors = supporting_factors
        self.risk_factors = risk_factors
        self.water_requirement_info = water_requirement_info
        self.climate_sensitivity_info = climate_sensitivity_info
        self.crop_calendar_info = crop_calendar_info
        self.missing_information = missing_information
        self.verification_status = verification_status
        self.explanation = explanation
        self.monitoring_considerations = monitoring_considerations
        self.comparative_score = comparative_score
        self.evidence_coverage_pct = evidence_coverage_pct
        self.uncertainty_level = uncertainty_level

    def to_dict(self) -> Dict[str, Any]:
        return {
            "crop_id": self.crop_id,
            "crop_name": self.crop_name,
            "priority": self.priority,
            "suitability_status": self.suitability_status,
            "assessment_period": self.assessment_period,
            "supporting_factors": self.supporting_factors,
            "risk_factors": self.risk_factors,
            "water_requirement_info": self.water_requirement_info,
            "climate_sensitivity_info": self.climate_sensitivity_info,
            "crop_calendar_info": self.crop_calendar_info,
            "missing_information": self.missing_information,
            "verification_status": self.verification_status,
            "explanation": self.explanation,
            "monitoring_considerations": self.monitoring_considerations,
            "comparative_score": self.comparative_score,
            "evidence_coverage_pct": self.evidence_coverage_pct,
            "uncertainty_level": self.uncertainty_level,
            "methodology_disclaimer": (
                "Comparative score is an exploratory software index (0-100) reflecting relative "
                "observational alignment, not a guaranteed agronomic yield prediction."
            )
        }
