import unittest

from router import RiskLevel, TaskType, route_task


class RouterTests(unittest.TestCase):
    def test_job_routing(self):
        result = route_task("Review this resume for a hiring decision")
        self.assertEqual(result.task_type, TaskType.JOB)
        self.assertEqual(result.suggested_agent, "job_machine")

    def test_strategy_routing(self):
        result = route_task("Create a go-to-market strategy for Q3")
        self.assertEqual(result.task_type, TaskType.STRATEGY)
        self.assertEqual(result.suggested_agent, "consultant")

    def test_financial_model_routing(self):
        result = route_task("Build a DCF valuation for this company")
        self.assertEqual(result.task_type, TaskType.FINANCIAL_MODEL)
        self.assertEqual(result.suggested_agent, "analyst")

    def test_research_routing(self):
        result = route_task("Research competitor pricing and compare offerings")
        self.assertEqual(result.task_type, TaskType.RESEARCH)

    def test_artifact_fallback(self):
        result = route_task("Please draft a short memo")
        self.assertEqual(result.task_type, TaskType.ARTIFACT)

    def test_high_risk_keywords(self):
        result = route_task("Need analysis for a compliance audit")
        self.assertEqual(result.risk_level, RiskLevel.HIGH)
        self.assertTrue(result.needs_verification)

    def test_medium_risk_keywords(self):
        result = route_task("Prepare strategy for a product launch")
        self.assertEqual(result.risk_level, RiskLevel.MED)
        self.assertTrue(result.needs_verification)

    def test_low_risk_default(self):
        result = route_task("Write a project update document")
        self.assertEqual(result.risk_level, RiskLevel.LOW)
        self.assertFalse(result.needs_verification)

    def test_explicit_risk_override(self):
        result = route_task("Simple request", metadata={"risk_level": "HIGH"})
        self.assertEqual(result.risk_level, RiskLevel.HIGH)

    def test_explicit_verification_override(self):
        result = route_task(
            "Need compliance research",
            metadata={"needs_verification": False},
        )
        self.assertEqual(result.risk_level, RiskLevel.HIGH)
        self.assertFalse(result.needs_verification)

    def test_metadata_influences_task(self):
        result = route_task("Need help", metadata={"notes": "financial model"})
        self.assertEqual(result.task_type, TaskType.FINANCIAL_MODEL)


if __name__ == "__main__":
    unittest.main()
