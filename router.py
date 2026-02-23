from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping


class TaskType(Enum):
    JOB = "JOB"
    STRATEGY = "STRATEGY"
    FINANCIAL_MODEL = "FINANCIAL_MODEL"
    RESEARCH = "RESEARCH"
    ARTIFACT = "ARTIFACT"


class RiskLevel(Enum):
    LOW = "LOW"
    MED = "MED"
    HIGH = "HIGH"


@dataclass(frozen=True)
class TaskRoute:
    task_type: TaskType
    risk_level: RiskLevel
    needs_verification: bool
    suggested_agent: str


_TASK_KEYWORDS: dict[TaskType, tuple[str, ...]] = {
    TaskType.FINANCIAL_MODEL: (
        "financial model",
        "forecast",
        "projection",
        "valuation",
        "discounted cash flow",
        "dcf",
        "budget model",
        "cash flow",
        "revenue model",
    ),
    TaskType.STRATEGY: (
        "strategy",
        "roadmap",
        "go-to-market",
        "gtm",
        "positioning",
        "market entry",
        "competitive strategy",
        "prioritization",
    ),
    TaskType.RESEARCH: (
        "research",
        "investigate",
        "analyze",
        "analysis",
        "benchmark",
        "literature review",
        "compare",
    ),
    TaskType.JOB: (
        "job",
        "hiring",
        "resume",
        "cv",
        "candidate",
        "interview",
        "recruit",
        "cover letter",
    ),
    TaskType.ARTIFACT: (
        "artifact",
        "document",
        "deck",
        "slide",
        "presentation",
        "memo",
        "report",
        "spec",
        "write up",
    ),
}

_RISK_KEYWORDS_HIGH = (
    "legal",
    "compliance",
    "regulatory",
    "lawsuit",
    "security",
    "breach",
    "sensitive",
    "confidential",
    "board",
    "audit",
)

_RISK_KEYWORDS_MED = (
    "budget",
    "finance",
    "financial",
    "pricing",
    "contract",
    "customer",
    "deadline",
    "launch",
)

_AGENT_BY_TASK: dict[TaskType, str] = {
    TaskType.JOB: "job_machine",
    TaskType.STRATEGY: "consultant",
    TaskType.FINANCIAL_MODEL: "analyst",
    TaskType.RESEARCH: "analyst",
    TaskType.ARTIFACT: "consultant",
}


def route_task(request: str, metadata: Mapping[str, Any] | None = None) -> TaskRoute:
    """Route a task request to a task type, risk level, and suggested agent.

    Routing is deterministic and based on simple keyword heuristics across
    request text and flattened metadata content.
    """

    metadata = metadata or {}
    corpus = _build_corpus(request, metadata)

    task_type = _infer_task_type(corpus)
    risk_level = _infer_risk_level(corpus, metadata)

    explicit_verification = metadata.get("needs_verification")
    if isinstance(explicit_verification, bool):
        needs_verification = explicit_verification
    else:
        needs_verification = risk_level in {RiskLevel.MED, RiskLevel.HIGH}

    return TaskRoute(
        task_type=task_type,
        risk_level=risk_level,
        needs_verification=needs_verification,
        suggested_agent=_AGENT_BY_TASK[task_type],
    )


def _build_corpus(request: str, metadata: Mapping[str, Any]) -> str:
    metadata_blob = " ".join(f"{k} {v}" for k, v in sorted(metadata.items()))
    return f"{request} {metadata_blob}".lower()


def _infer_task_type(corpus: str) -> TaskType:
    for task_type in (
        TaskType.FINANCIAL_MODEL,
        TaskType.STRATEGY,
        TaskType.RESEARCH,
        TaskType.JOB,
        TaskType.ARTIFACT,
    ):
        if any(keyword in corpus for keyword in _TASK_KEYWORDS[task_type]):
            return task_type
    return TaskType.ARTIFACT


def _infer_risk_level(corpus: str, metadata: Mapping[str, Any]) -> RiskLevel:
    risk_override = str(metadata.get("risk_level", "")).strip().upper()
    if risk_override in {level.value for level in RiskLevel}:
        return RiskLevel[risk_override]

    if any(keyword in corpus for keyword in _RISK_KEYWORDS_HIGH):
        return RiskLevel.HIGH
    if any(keyword in corpus for keyword in _RISK_KEYWORDS_MED):
        return RiskLevel.MED
    return RiskLevel.LOW
