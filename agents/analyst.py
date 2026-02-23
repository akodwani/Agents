"""Analyst pipeline orchestrating Architect, Executor, and Auditor stages."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict

from tools.model_auditor import audit_model_results
from tools.model_executor import execute_model


@dataclass
class PipelineResult:
    assumptions_json: str
    model_schema: Dict[str, Any]
    model_outputs: Dict[str, Any]
    audit_report: Dict[str, Any]


def build_assumptions(company_snapshot: Dict[str, Any]) -> tuple[str, Dict[str, Any]]:
    """Stage A (Architect): Build assumption scenarios and schema as valid JSON.

    Args:
        company_snapshot: Basic company inputs such as revenue and margin profile.

    Returns:
        Tuple of (assumptions_json, model_schema).
    """
    revenue = float(company_snapshot.get("revenue", 100.0))
    growth = float(company_snapshot.get("growth_rate", 0.1))
    ebitda_margin = float(company_snapshot.get("ebitda_margin", 0.2))
    tax_rate = float(company_snapshot.get("tax_rate", 0.25))
    discount_rate = float(company_snapshot.get("discount_rate", 0.1))
    terminal_growth = float(company_snapshot.get("terminal_growth", 0.02))

    assumptions = {
        "base": {
            "revenue": revenue,
            "growth_rate": growth,
            "ebitda_margin": ebitda_margin,
            "tax_rate": tax_rate,
            "discount_rate": discount_rate,
            "terminal_growth": terminal_growth,
        },
        "high": {
            "revenue": revenue * 1.05,
            "growth_rate": growth + 0.03,
            "ebitda_margin": min(0.6, ebitda_margin + 0.03),
            "tax_rate": max(0.05, tax_rate - 0.01),
            "discount_rate": max(0.06, discount_rate - 0.01),
            "terminal_growth": terminal_growth + 0.005,
        },
        "low": {
            "revenue": revenue * 0.95,
            "growth_rate": growth - 0.03,
            "ebitda_margin": max(0.0, ebitda_margin - 0.03),
            "tax_rate": min(0.4, tax_rate + 0.01),
            "discount_rate": discount_rate + 0.01,
            "terminal_growth": max(-0.01, terminal_growth - 0.005),
        },
    }

    model_schema = {
        "type": "object",
        "required": ["base", "high", "low"],
        "properties": {
            scenario: {
                "type": "object",
                "required": [
                    "revenue",
                    "growth_rate",
                    "ebitda_margin",
                    "tax_rate",
                    "discount_rate",
                    "terminal_growth",
                ],
                "properties": {
                    "revenue": {"type": "number", "minimum": 0},
                    "growth_rate": {"type": "number", "minimum": -0.2, "maximum": 1.0},
                    "ebitda_margin": {"type": "number", "minimum": 0.0, "maximum": 0.6},
                    "tax_rate": {"type": "number", "minimum": 0.0, "maximum": 0.6},
                    "discount_rate": {"type": "number", "minimum": 0.0, "maximum": 0.5},
                    "terminal_growth": {"type": "number", "minimum": -0.02, "maximum": 0.1},
                },
            }
            for scenario in ("base", "high", "low")
        },
    }

    assumptions_json = json.dumps(assumptions)
    return assumptions_json, model_schema


def run_analyst_pipeline(company_snapshot: Dict[str, Any], model_type: str = "dcf") -> PipelineResult:
    """Run all three stages and return outputs."""
    assumptions_json, schema = build_assumptions(company_snapshot)
    outputs = execute_model(assumptions_json=assumptions_json, model_type=model_type)
    audit = audit_model_results(outputs["metrics_df"])  # type: ignore[index]

    return PipelineResult(
        assumptions_json=assumptions_json,
        model_schema=schema,
        model_outputs=outputs,
        audit_report=audit,
    )
