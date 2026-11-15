"""
decision_support.explanation_engine
Generates human-readable, agronomy-backed explanations for crop suitability and risk factors.
Transparently articulates evidence, limits, and monitoring considerations without false guarantees.
"""
from typing import Dict, List, Any

class ExplanationEngine:
    @staticmethod
    def generate_explanation(
        crop_name: str,
        suitability_status: str,
        supporting_factors: List[str],
        risk_factors: List[str],
        missing_information: List[str]
    ) -> str:
        """Formats an explainable natural language rationale grounded in empirical data."""
        lines = []
        lines.append(f"Assessment for {crop_name}: Classified as '{suitability_status}'.")
        
        if supporting_factors:
            lines.append("Key Supporting Observations:")
            for f in supporting_factors:
                lines.append(f"  • {f}")
        else:
            lines.append("No strong positive climate alignment observed for this period.")

        if risk_factors:
            lines.append("Documented Risk Factors & Vulnerabilities:")
            for r in risk_factors:
                lines.append(f"  • {r}")
        else:
            lines.append("No immediate severe empirical climate anomalies noted.")

        if missing_information:
            lines.append("Information Not Covered by Dataset (Requires Farm-Level Verification):")
            for m in missing_information:
                lines.append(f"  • {m}")

        lines.append("Note: Suitability status is an advisory screening metric based on 2020-2025 observations; it does not guarantee yield or eliminate agronomic hazards.")
        return "\n".join(lines)
