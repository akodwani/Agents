from pathlib import Path

from agents.pipeline import (
    run_analyst,
    run_consultant,
    run_council_aggregation,
    run_job_machine,
    trigger_verification,
)


def test_council_aggregation_disagreement_types_behave():
    members = [
        {"name": "A", "vote": "approve", "confidence": "high", "rationale": "risk low"},
        {"name": "B", "vote": "reject", "confidence": "medium", "rationale": "risk medium"},
        {"name": "C", "vote": "approve", "confidence": "high", "rationale": "risk low"},
    ]

    result = run_council_aggregation(members)

    assert result["member_count"] == 3
    assert "outcome_disagreement" in result["disagreement_types"]
    assert "confidence_disagreement" in result["disagreement_types"]
    assert "rationale_disagreement" in result["disagreement_types"]


def test_job_machine_rejects_at_least_one_of_three_jds():
    jds = [
        "Senior backend engineer with benefits and standard hours",
        "Commission only sales role, no benefits",
        "Product manager with hybrid setup",
    ]

    decisions = run_job_machine(jds)
    rejects = [item for item in decisions if item["decision"] == "reject"]

    assert len(decisions) == 3
    assert len(rejects) >= 1


def test_consultant_includes_decision_forcer_sections():
    output = run_consultant("Improve hiring speed by 20%")

    assert "## Decision Forcer" in output
    assert "## Decision Forcer: Constraints" in output


def test_analyst_creates_xlsx_output(tmp_path: Path):
    output = tmp_path / "analysis" / "report.xlsx"
    created_path = run_analyst({"conversion": "12%", "retention": "89%"}, output)

    assert created_path.exists()
    assert created_path.suffix == ".xlsx"
    assert created_path.stat().st_size > 0


def test_verification_writes_jsonl_when_triggered(tmp_path: Path):
    output = tmp_path / "verify_events.jsonl"
    events = [
        {"event": "verification_started", "status": "ok"},
        {"event": "verification_completed", "status": "ok"},
    ]

    created_path = trigger_verification(events, output)

    assert created_path.exists()
    lines = created_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2
    assert "verification_started" in lines[0]
