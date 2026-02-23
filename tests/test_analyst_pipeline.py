import json
from pathlib import Path
import unittest

from agents.analyst import build_assumptions, run_analyst_pipeline
from tools.model_auditor import audit_model_results


class TestAnalystPipeline(unittest.TestCase):
    def setUp(self) -> None:
        self.snapshot = {
            "company": "SampleCo",
            "revenue": 250.0,
            "growth_rate": 0.12,
            "ebitda_margin": 0.28,
            "tax_rate": 0.23,
            "discount_rate": 0.1,
            "terminal_growth": 0.025,
        }

    def test_stage_a_returns_valid_json_and_schema(self):
        assumptions_json, schema = build_assumptions(self.snapshot)
        assumptions = json.loads(assumptions_json)
        self.assertEqual(set(assumptions.keys()), {"base", "high", "low"})
        self.assertEqual(schema["type"], "object")
        self.assertIn("properties", schema)

    def test_pipeline_produces_xlsx_and_runs_audits(self):
        result = run_analyst_pipeline(self.snapshot, model_type="dcf")

        xlsx_path = Path(result.model_outputs["xlsx_path"])
        self.assertTrue(xlsx_path.exists(), "Expected XLSX output file to be created")
        self.assertGreater(result.audit_report["issue_count"], -1)

    def test_auditor_flags_out_of_bounds(self):
        result = run_analyst_pipeline(self.snapshot, model_type="dcf")
        metrics_df = result.model_outputs["metrics_df"].copy()
        metrics_df.loc[0, "ebitda_margin"] = 0.9
        metrics_df.loc[1, "growth_rate"] = 1.3

        audit_report = audit_model_results(metrics_df)
        self.assertFalse(audit_report["is_clean"])
        self.assertGreaterEqual(audit_report["issue_count"], 2)


if __name__ == "__main__":
    unittest.main()
