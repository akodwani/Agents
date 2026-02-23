from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class BudgetSnapshot:
    remaining_daily: float
    remaining_monthly: float


class BudgetManager:
    """Tracks spend by task type and date and writes usage as JSONL logs."""

    def __init__(
        self,
        daily_budget: float,
        monthly_budget: float,
        log_path: str = "logs/spending_log.jsonl",
    ) -> None:
        self.daily_budget = float(daily_budget)
        self.monthly_budget = float(monthly_budget)
        self.log_path = Path(log_path)

        self.task_spend: Dict[str, float] = {}
        self.daily_spend: Dict[str, float] = {}
        self.monthly_spend: Dict[str, float] = {}

        self._ensure_log_parent()
        self._hydrate_from_log()

    def _ensure_log_parent(self) -> None:
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def _hydrate_from_log(self) -> None:
        if not self.log_path.exists():
            return

        with self.log_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue

                timestamp = entry.get("timestamp")
                task_type = entry.get("task_type", "unknown")
                cost = float(entry.get("estimated_cost", 0.0))

                dt = self._parse_timestamp(timestamp)
                self._accumulate(cost=cost, task_type=task_type, when=dt)

    def _parse_timestamp(self, timestamp: Optional[str]) -> datetime:
        if not timestamp:
            return datetime.now(timezone.utc)

        try:
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
        except ValueError:
            return datetime.now(timezone.utc)

    def _accumulate(self, cost: float, task_type: str, when: datetime) -> None:
        day_key = when.strftime("%Y-%m-%d")
        month_key = when.strftime("%Y-%m")

        self.task_spend[task_type] = self.task_spend.get(task_type, 0.0) + cost
        self.daily_spend[day_key] = self.daily_spend.get(day_key, 0.0) + cost
        self.monthly_spend[month_key] = self.monthly_spend.get(month_key, 0.0) + cost

    def estimate_cost_placeholder(self, input_tokens: int, output_tokens: int) -> float:
        """Placeholder cost estimate until provider-specific pricing is added."""
        return ((input_tokens + output_tokens) / 1000.0) * 0.001

    def check_budget(self, now: Optional[datetime] = None) -> Dict[str, float]:
        now = now or datetime.now(timezone.utc)
        day_key = now.strftime("%Y-%m-%d")
        month_key = now.strftime("%Y-%m")

        daily_used = self.daily_spend.get(day_key, 0.0)
        monthly_used = self.monthly_spend.get(month_key, 0.0)

        remaining_daily = max(0.0, self.daily_budget - daily_used)
        remaining_monthly = max(0.0, self.monthly_budget - monthly_used)

        return {
            "remaining_daily": remaining_daily,
            "remaining_monthly": remaining_monthly,
        }

    def record_usage(
        self,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        estimated_cost: float,
        task_type: str,
    ) -> Dict[str, float]:
        now = datetime.now(timezone.utc)

        entry = {
            "timestamp": now.isoformat(),
            "provider": provider,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "estimated_cost": float(estimated_cost),
            "task_type": task_type,
        }

        with self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry) + "\n")

        self._accumulate(cost=float(estimated_cost), task_type=task_type, when=now)
        return self.check_budget(now=now)
