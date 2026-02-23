import json
import tempfile
import unittest
from pathlib import Path

from council import DisagreementType, MemberResponse, classify_disagreement, council_run


class AggregatorClassificationTests(unittest.TestCase):
    def test_none_when_answers_match(self):
        responses = [
            MemberResponse("same", ["a"], "go", 0.8, [], False),
            MemberResponse("same", ["a"], "go", 0.7, [], False),
        ]
        self.assertEqual(classify_disagreement(responses), DisagreementType.NONE)

    def test_fact_disagreement(self):
        responses = [
            MemberResponse("similar wording", ["earth is round"], "go", 0.8, [], False),
            MemberResponse("different wording", ["earth is flat"], "go", 0.7, [], False),
        ]
        self.assertEqual(classify_disagreement(responses), DisagreementType.FACT_DISAGREE)

    def test_numeric_disagreement(self):
        responses = [
            MemberResponse("Revenue is 100", ["same fact"], "forecast 100", 0.8, [], False),
            MemberResponse("Revenue is 120", ["same fact"], "forecast 120", 0.7, [], False),
        ]
        self.assertEqual(classify_disagreement(responses), DisagreementType.NUMERIC_DISAGREE)

    def test_style_disagreement(self):
        responses = [
            MemberResponse("Use a friendly tone", ["same fact"], "Proceed", 0.8, [], False),
            MemberResponse("Please proceed kindly", ["same fact"], "Proceed", 0.7, [], False),
        ]
        self.assertEqual(classify_disagreement(responses), DisagreementType.STYLE_DISAGREE)


class CouncilRunVerificationTests(unittest.TestCase):
    def _adapter(self, answer, findings, recommendation, confidence=0.5):
        def _inner(member_id, prompt, context):
            return json.dumps(
                {
                    "answer": answer,
                    "key_findings": findings,
                    "recommendation": recommendation,
                    "confidence": confidence,
                    "risks": [],
                    "contrarian": False,
                }
            )

        return _inner

    def test_logs_when_verification_called(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            result = council_run(
                "analysis",
                "prompt",
                {
                    "agreement_threshold": 0.9,
                    "verify_budget_remaining": 1,
                    "logs_dir": tmp_dir,
                    "member_adapters": [
                        self._adapter("A is true", ["fact one"], "yes"),
                        self._adapter("B is true", ["fact two"], "no"),
                    ],
                },
            )
            self.assertTrue(result.verification_called)
            log_file = Path(tmp_dir) / "verify_events.jsonl"
            self.assertTrue(log_file.exists())
            lines = log_file.read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(lines), 1)
            self.assertIn('"decision": "called"', lines[0])

    def test_logs_when_verification_skipped_due_to_budget(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            result = council_run(
                "analysis",
                "prompt",
                {
                    "agreement_threshold": 0.9,
                    "verify_budget_remaining": 0,
                    "logs_dir": tmp_dir,
                    "member_adapters": [
                        self._adapter("A is true", ["fact one"], "yes"),
                        self._adapter("B is true", ["fact two"], "no"),
                    ],
                },
            )
            self.assertFalse(result.verification_called)
            log_file = Path(tmp_dir) / "verify_events.jsonl"
            self.assertTrue(log_file.exists())
            lines = log_file.read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(lines), 1)
            self.assertIn('"decision": "skipped_budget"', lines[0])


if __name__ == "__main__":
    unittest.main()
