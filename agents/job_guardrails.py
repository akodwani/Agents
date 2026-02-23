from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable
import re


@dataclass
class GuardrailDecision:
    hard_reject_reasons: list[str] = field(default_factory=list)
    low_signal_reasons: list[str] = field(default_factory=list)
    proceed: bool = False
    scores: dict[str, int] = field(default_factory=lambda: {
        "fit_score": 0,
        "role_quality_score": 0,
        "company_signal_score": 0,
    })


def _contains_any(text: str, patterns: Iterable[str]) -> bool:
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)


def _bounded_score(value: int) -> int:
    return max(0, min(100, int(value)))


def evaluate_job(jd_text: str, constraints: Dict[str, Any] | None = None) -> GuardrailDecision:
    """Evaluate a job description against quality and fit guardrails.

    Args:
        jd_text: Raw job description text.
        constraints: Optional preference dict supporting:
            - target_roles: list[str]
            - required_keywords: list[str]
            - min_salary: int (annual USD)
            - disallow_contract: bool
            - disallow_hybrid_or_onsite: bool

    Returns:
        GuardrailDecision with per-dimension scores and reasons.
    """
    constraints = constraints or {}
    text = (jd_text or "").strip()
    lowered = text.lower()
    decision = GuardrailDecision()

    if not text:
        decision.hard_reject_reasons.append("empty_job_description")

    hard_reject_patterns = {
        "commission_only_compensation": [
            r"commission\s*only",
            r"100%\s*commission",
            r"unlimited\s*commission\s*only",
        ],
        "pay_to_apply_or_training_fee": [
            r"pay\s+for\s+training",
            r"application\s+fee",
            r"upfront\s+fee",
            r"starter\s+kit\s+required",
        ],
        "mlm_or_pyramid_language": [
            r"multi-?level\s+marketing",
            r"recruit\s+your\s+own\s+team\s+to\s+earn",
            r"pyramid\s+scheme",
        ],
    }

    for reason, patterns in hard_reject_patterns.items():
        if _contains_any(lowered, patterns):
            decision.hard_reject_reasons.append(reason)

    # Role quality signal.
    role_quality = 30
    if len(text) > 400:
        role_quality += 15
    if _contains_any(lowered, [r"responsibilit", r"what\s+you('|\s)ll\s+do", r"day\s*to\s*day"]):
        role_quality += 20
    if _contains_any(lowered, [r"requirements", r"qualifications", r"must\s+have"]):
        role_quality += 20
    if _contains_any(lowered, [r"benefits", r"health", r"401\(k\)", r"pto"]):
        role_quality += 15
    if _contains_any(lowered, [r"urgent\s+hiring", r"easy\s+money", r"no\s+experience\s+needed"]):
        role_quality -= 25
        decision.low_signal_reasons.append("hype_or_low_credibility_language")

    # Company signal.
    company_signal = 25
    if _contains_any(lowered, [r"about\s+us", r"founded\s+in", r"our\s+mission"]):
        company_signal += 20
    if _contains_any(lowered, [r"[\w.+-]+@[\w-]+\.[\w.-]+", r"https?://", r"www\."]):
        company_signal += 20
    if _contains_any(lowered, [r"series\s+[abc]", r"publicly\s+traded", r"fortune\s+\d+"]):
        company_signal += 15
    if _contains_any(lowered, [r"stealth\s+startup", r"confidential\s+company\s+name"]):
        company_signal -= 15
        decision.low_signal_reasons.append("company_identity_opaque")

    # Fit score from constraints.
    fit_score = 50
    target_roles = [r.lower() for r in constraints.get("target_roles", [])]
    if target_roles:
        if any(role in lowered for role in target_roles):
            fit_score += 20
        else:
            fit_score -= 20
            decision.low_signal_reasons.append("role_mismatch")

    required_keywords = [kw.lower() for kw in constraints.get("required_keywords", [])]
    missing_keywords = [kw for kw in required_keywords if kw not in lowered]
    if required_keywords:
        fit_score += max(0, 20 - 8 * len(missing_keywords))
        if missing_keywords:
            decision.low_signal_reasons.append("missing_required_keywords")

    salary_match = re.search(r"\$\s?([\d,]{2,})\s?(?:-|to)\s?\$\s?([\d,]{2,})", text)
    if salary_match and constraints.get("min_salary"):
        low = int(salary_match.group(1).replace(",", ""))
        if low < int(constraints["min_salary"]):
            decision.low_signal_reasons.append("salary_below_minimum")
            fit_score -= 20
        else:
            fit_score += 10
    elif constraints.get("min_salary"):
        decision.low_signal_reasons.append("salary_not_disclosed")

    if constraints.get("disallow_contract") and _contains_any(lowered, [r"contract", r"1099", r"independent contractor"]):
        decision.hard_reject_reasons.append("contract_role_disallowed")

    if constraints.get("disallow_hybrid_or_onsite") and _contains_any(lowered, [r"hybrid", r"on-?site", r"in\s+office"]):
        decision.hard_reject_reasons.append("work_location_disallowed")

    decision.scores = {
        "fit_score": _bounded_score(fit_score),
        "role_quality_score": _bounded_score(role_quality),
        "company_signal_score": _bounded_score(company_signal),
    }

    average_score = sum(decision.scores.values()) / 3
    if average_score < 45:
        decision.low_signal_reasons.append("overall_signal_too_low")

    decision.low_signal_reasons = sorted(set(decision.low_signal_reasons))
    decision.hard_reject_reasons = sorted(set(decision.hard_reject_reasons))

    decision.proceed = not decision.hard_reject_reasons and average_score >= 50
    return decision
