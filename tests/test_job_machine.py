import unittest

from agents.job_machine import run_job_pipeline


GOOD_DATA_ENGINEER_JD = """
Senior Data Engineer
Company: Northstar Analytics
Location: Remote (US)
Compensation: $150,000 - $185,000

About us: Northstar Analytics helps healthcare providers improve outcomes through data products.
Responsibilities:
- Build and maintain data pipelines using Python, SQL, and AWS.
- Partner with product and stakeholder teams to deliver reporting and ML features.
Requirements:
- 5+ years of data engineering experience.
- Production experience with Python, SQL, Docker.
Benefits: medical, dental, vision, 401(k), flexible PTO.
Contact: jobs@northstaranalytics.com
"""

LOW_SIGNAL_JD = """
Rockstar Builder Wanted!!!
Earn fast and start today.
No experience needed. Urgent hiring.
"""

COMMISSION_SPAM_JD = """
Sales Opportunity - Work from Anywhere
This is a 100% commission only role with unlimited upside.
Starter kit required to begin.
Recruit your own team to earn more.
"""

ONSITE_CONTRACT_JD = """
Backend Engineer
Company: CityCore Systems
Location: On-site, Austin TX
Contract role (1099) for 12 months.
Responsibilities include Python API development and SQL optimization.
Compensation: $90,000 - $110,000
"""

MISSING_KEYWORDS_JD = """
Product Analyst
Company: Meridian Retail
Location: Hybrid - Chicago
Compensation: $130,000 - $150,000

About us: We are a public retail company modernizing our digital channels.
Responsibilities:
- Analyze product funnel metrics and communicate trends.
Requirements:
- 4+ years in analytics, experimentation, and stakeholder communication.
Benefits: health, 401(k), PTO.
"""


class JobMachineTests(unittest.TestCase):
    def test_pipeline_proceeds_for_high_quality_jd(self):
        result = run_job_pipeline(
            GOOD_DATA_ENGINEER_JD,
            constraints={
                "target_roles": ["data engineer"],
                "required_keywords": ["python", "sql", "aws"],
                "min_salary": 140000,
            },
            candidate_profile={"skills": ["python", "sql"]},
        )
        self.assertEqual(result["stage"], "drafts_ready")
        self.assertTrue(result["decision"]["proceed"])
        self.assertIn("resume_edits", result)
        self.assertIn("linkedin_message", result)

    def test_low_signal_jd_is_rejected(self):
        result = run_job_pipeline(LOW_SIGNAL_JD, constraints={"target_roles": ["data engineer"]})
        self.assertEqual(result["stage"], "rejected")
        self.assertFalse(result["decision"]["proceed"])
        self.assertIn("overall_signal_too_low", result["decision"]["low_signal_reasons"])

    def test_commission_only_jd_is_hard_rejected(self):
        result = run_job_pipeline(COMMISSION_SPAM_JD)
        self.assertEqual(result["stage"], "rejected")
        self.assertIn("commission_only_compensation", result["decision"]["hard_reject_reasons"])

    def test_constraint_based_hard_rejection(self):
        result = run_job_pipeline(
            ONSITE_CONTRACT_JD,
            constraints={"disallow_contract": True, "disallow_hybrid_or_onsite": True},
        )
        self.assertEqual(result["stage"], "rejected")
        self.assertIn("contract_role_disallowed", result["decision"]["hard_reject_reasons"])
        self.assertIn("work_location_disallowed", result["decision"]["hard_reject_reasons"])

    def test_missing_required_keywords_flagged(self):
        result = run_job_pipeline(
            MISSING_KEYWORDS_JD,
            constraints={
                "target_roles": ["product analyst"],
                "required_keywords": ["sql", "python", "aws"],
                "min_salary": 120000,
            },
        )
        self.assertIn("missing_required_keywords", result["decision"]["low_signal_reasons"])


if __name__ == "__main__":
    unittest.main()
