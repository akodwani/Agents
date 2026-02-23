from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Callable


class DisagreementType(str, Enum):
    FACT_DISAGREE = "FACT_DISAGREE"
    STRUCTURE_DISAGREE = "STRUCTURE_DISAGREE"
    NUMERIC_DISAGREE = "NUMERIC_DISAGREE"
    STYLE_DISAGREE = "STYLE_DISAGREE"
    NONE = "NONE"


@dataclass
class MemberResponse:
    answer: str
    key_findings: list[str]
    recommendation: str
    confidence: float
    risks: list[str]
    contrarian: bool


@dataclass
class CouncilResult:
    member_responses: list[MemberResponse]
    agreement_score: float
    disagreement_type: DisagreementType
    final_answer: str
    verification_called: bool


MemberAdapter = Callable[[str, str, dict[str, Any]], str]


def _default_member_adapter(member_id: str, prompt: str, context: dict[str, Any]) -> str:
    """Stub adapter that simulates a model member and returns strict JSON."""
    response = {
        "answer": f"[{member_id}] {prompt}",
        "key_findings": [f"{member_id} processed prompt"],
        "recommendation": "Proceed with caution.",
        "confidence": 0.6,
        "risks": ["Stub response"],
        "contrarian": False,
    }
    return json.dumps(response)


def _parse_member_json(raw_json: str) -> MemberResponse:
    parsed = json.loads(raw_json)
    required_fields = {
        "answer",
        "key_findings",
        "recommendation",
        "confidence",
        "risks",
        "contrarian",
    }
    missing = required_fields - set(parsed.keys())
    if missing:
        raise ValueError(f"Missing required fields: {sorted(missing)}")

    confidence = float(parsed["confidence"])
    if not 0.0 <= confidence <= 1.0:
        raise ValueError("confidence must be between 0 and 1")

    return MemberResponse(
        answer=str(parsed["answer"]),
        key_findings=[str(item) for item in parsed["key_findings"]],
        recommendation=str(parsed["recommendation"]),
        confidence=confidence,
        risks=[str(item) for item in parsed["risks"]],
        contrarian=bool(parsed["contrarian"]),
    )


def _extract_numbers(text: str) -> list[float]:
    numbers: list[float] = []
    current = ""
    for char in text:
        if char.isdigit() or char in {".", "-"}:
            current += char
        elif current:
            try:
                numbers.append(float(current))
            except ValueError:
                pass
            current = ""
    if current:
        try:
            numbers.append(float(current))
        except ValueError:
            pass
    return numbers


def _normalize_fact_set(items: list[str]) -> set[str]:
    return {item.strip().lower() for item in items if item.strip()}


def classify_disagreement(member_responses: list[MemberResponse]) -> DisagreementType:
    if not member_responses:
        return DisagreementType.NONE

    answers = [m.answer.strip().lower() for m in member_responses]
    if len(set(answers)) == 1:
        return DisagreementType.NONE

    findings_sets = [_normalize_fact_set(m.key_findings) for m in member_responses]
    if len({frozenset(facts) for facts in findings_sets}) > 1:
        return DisagreementType.FACT_DISAGREE

    recs = [m.recommendation.strip().lower() for m in member_responses]
    if len(set(recs)) > 1:
        if {"yes", "no"}.issubset(set(recs)):
            return DisagreementType.STRUCTURE_DISAGREE

    numeric_signatures = [tuple(_extract_numbers(m.answer + " " + m.recommendation)) for m in member_responses]
    if len(set(numeric_signatures)) > 1:
        return DisagreementType.NUMERIC_DISAGREE

    return DisagreementType.STYLE_DISAGREE


def calculate_agreement_score(member_responses: list[MemberResponse]) -> float:
    if not member_responses:
        return 1.0

    total_pairs = 0
    matching_pairs = 0
    for i in range(len(member_responses)):
        for j in range(i + 1, len(member_responses)):
            total_pairs += 1
            left = member_responses[i]
            right = member_responses[j]
            if (
                left.answer.strip().lower() == right.answer.strip().lower()
                and _normalize_fact_set(left.key_findings) == _normalize_fact_set(right.key_findings)
                and left.recommendation.strip().lower() == right.recommendation.strip().lower()
            ):
                matching_pairs += 1

    if total_pairs == 0:
        return 1.0
    return matching_pairs / total_pairs


def synthesize_final_answer(member_responses: list[MemberResponse]) -> str:
    if not member_responses:
        return ""

    sorted_members = sorted(member_responses, key=lambda item: item.confidence, reverse=True)
    top = sorted_members[0]
    consensus_findings: list[str] = []
    seen: set[str] = set()
    for member in sorted_members:
        for finding in member.key_findings:
            norm = finding.strip().lower()
            if norm and norm not in seen:
                seen.add(norm)
                consensus_findings.append(finding.strip())

    findings_text = "; ".join(consensus_findings[:5]) if consensus_findings else "No shared findings"
    return (
        f"Answer: {top.answer}\n"
        f"Recommendation: {top.recommendation}\n"
        f"Key findings: {findings_text}"
    )


def verify(member_responses: list[MemberResponse], prompt: str, context: dict[str, Any]) -> dict[str, Any]:
    """Stubbed verification step."""
    return {
        "status": "verified",
        "checked_claims": sum(len(m.key_findings) for m in member_responses),
        "prompt": prompt,
    }


def _append_verify_event(event: dict[str, Any], logs_dir: Path) -> None:
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_path = logs_dir / "verify_events.jsonl"
    with log_path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(event) + "\n")


def council_run(task_type: str, prompt: str, context: dict[str, Any] | None = None) -> CouncilResult:
    context = context or {}
    threshold = float(context.get("agreement_threshold", 0.65))
    budget_remaining = int(context.get("verify_budget_remaining", 1))
    logs_dir = Path(context.get("logs_dir", "logs"))

    member_adapters: list[MemberAdapter] = context.get("member_adapters", [])
    if not member_adapters:
        n_members = int(context.get("n_members", 3))
        member_adapters = [_default_member_adapter for _ in range(n_members)]

    with ThreadPoolExecutor(max_workers=len(member_adapters)) as pool:
        futures = [
            pool.submit(adapter, f"member-{index + 1}", prompt, context)
            for index, adapter in enumerate(member_adapters)
        ]
        raw_outputs = [future.result() for future in futures]

    member_responses = [_parse_member_json(raw) for raw in raw_outputs]
    disagreement_type = classify_disagreement(member_responses)
    agreement_score = calculate_agreement_score(member_responses)

    escalation_candidates = {
        DisagreementType.FACT_DISAGREE,
        DisagreementType.STRUCTURE_DISAGREE,
        DisagreementType.NUMERIC_DISAGREE,
    }
    should_consider_verify = disagreement_type in escalation_candidates and agreement_score < threshold

    verification_called = False
    if should_consider_verify:
        if budget_remaining > 0:
            verify(member_responses, prompt, context)
            verification_called = True
            decision = "called"
        else:
            decision = "skipped_budget"

        _append_verify_event(
            {
                "task_type": task_type,
                "disagreement_type": disagreement_type.value,
                "agreement_score": agreement_score,
                "threshold": threshold,
                "decision": decision,
                "verification_called": verification_called,
            },
            logs_dir=logs_dir,
        )

    final_answer = synthesize_final_answer(member_responses)
    return CouncilResult(
        member_responses=member_responses,
        agreement_score=agreement_score,
        disagreement_type=disagreement_type,
        final_answer=final_answer,
        verification_called=verification_called,
    )


__all__ = [
    "CouncilResult",
    "DisagreementType",
    "MemberResponse",
    "calculate_agreement_score",
    "classify_disagreement",
    "council_run",
    "synthesize_final_answer",
    "verify",
]
