import json
from datetime import datetime, timezone

from budget import BudgetManager


def test_record_usage_writes_jsonl_log(tmp_path):
    log_path = tmp_path / "logs" / "spending_log.jsonl"
    manager = BudgetManager(daily_budget=10.0, monthly_budget=100.0, log_path=str(log_path))

    manager.record_usage(
        provider="openai",
        model="gpt-test",
        input_tokens=100,
        output_tokens=50,
        estimated_cost=1.25,
        task_type="analysis",
    )

    assert log_path.exists()
    lines = log_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1

    row = json.loads(lines[0])
    assert row["provider"] == "openai"
    assert row["model"] == "gpt-test"
    assert row["estimated_cost"] == 1.25
    assert row["task_type"] == "analysis"


def test_check_budget_applies_caps_at_zero(tmp_path):
    log_path = tmp_path / "spending_log.jsonl"
    manager = BudgetManager(daily_budget=10.0, monthly_budget=100.0, log_path=str(log_path))

    manager.record_usage(
        provider="test",
        model="model",
        input_tokens=10,
        output_tokens=10,
        estimated_cost=15.0,
        task_type="task-a",
    )

    budget = manager.check_budget()
    assert budget["remaining_daily"] == 0.0
    assert budget["remaining_monthly"] == 85.0


def test_budget_depletion_and_task_tracking(tmp_path):
    log_path = tmp_path / "spending_log.jsonl"
    manager = BudgetManager(daily_budget=20.0, monthly_budget=25.0, log_path=str(log_path))

    manager.record_usage("test", "model", 10, 5, 10.0, "task-a")
    manager.record_usage("test", "model", 10, 5, 12.0, "task-b")
    manager.record_usage("test", "model", 10, 5, 5.0, "task-a")

    now = datetime.now(timezone.utc)
    budget = manager.check_budget(now=now)

    assert budget["remaining_daily"] == 0.0
    assert budget["remaining_monthly"] == 0.0
    assert manager.task_spend["task-a"] == 15.0
    assert manager.task_spend["task-b"] == 12.0
