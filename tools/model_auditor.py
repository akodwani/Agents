"""Stage C model auditor: sanity checks for generated scenario metrics."""

from __future__ import annotations

from typing import Any, Dict, List

import pandas as pd


def audit_model_results(metrics_df: pd.DataFrame) -> Dict[str, Any]:
    """Validate numeric bounds and flag issues with suggested fixes."""
    issues: List[Dict[str, str]] = []

    for _, row in metrics_df.iterrows():
        scenario = row["scenario"]

        if not (0.0 <= float(row["ebitda_margin"]) <= 0.6):
            issues.append(
                {
                    "scenario": scenario,
                    "field": "ebitda_margin",
                    "issue": "EBITDA margin out of sanity bounds (0-60%).",
                    "suggested_fix": "Clamp EBITDA margin into [0.0, 0.6] and review peer comps.",
                }
            )

        if not (-0.2 <= float(row["growth_rate"]) <= 1.0):
            issues.append(
                {
                    "scenario": scenario,
                    "field": "growth_rate",
                    "issue": "Growth rate out of sanity bounds (-20% to 100%).",
                    "suggested_fix": "Reassess growth drivers and normalize assumptions into [-0.2, 1.0].",
                }
            )

        if float(row["implied_value"]) <= 0:
            issues.append(
                {
                    "scenario": scenario,
                    "field": "implied_value",
                    "issue": "Implied value is non-positive.",
                    "suggested_fix": "Check discount rate vs terminal growth and operating assumptions.",
                }
            )

    return {
        "is_clean": len(issues) == 0,
        "issue_count": len(issues),
        "issues": issues,
    }
