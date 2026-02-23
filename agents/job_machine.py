from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Dict

from .job_guardrails import GuardrailDecision, evaluate_job


@dataclass
class JobParseResult:
    title: str
    company: str
    location: str
    salary_range: str
    jd_text: str


def parse_job_description(jd_text: str) -> JobParseResult:
    lines = [line.strip() for line in jd_text.splitlines() if line.strip()]
    title = ""
    company = ""
    location = ""
    salary_range = ""

    for line in lines[:8]:
        low = line.lower()
        if not title and any(x in low for x in ["engineer", "manager", "analyst", "developer", "designer", "specialist"]):
            title = line
        if not company and low.startswith("company"):
            company = line.split(":", 1)[-1].strip()
        if not location and low.startswith("location"):
            location = line.split(":", 1)[-1].strip()

    salary_match = re.search(r"\$\s?[\d,]{2,}\s?(?:-|to)\s?\$\s?[\d,]{2,}", jd_text)
    if salary_match:
        salary_range = salary_match.group(0)

    return JobParseResult(
        title=title or "Unknown title",
        company=company or "Unknown company",
        location=location or "Unknown location",
        salary_range=salary_range or "Not listed",
        jd_text=jd_text,
    )


def _resume_edits_from_jd(jd_text: str, candidate_profile: Dict[str, Any] | None) -> list[str]:
    candidate_profile = candidate_profile or {}
    existing_skills = {s.lower() for s in candidate_profile.get("skills", [])}
    suggestions: list[str] = []

    keywords = [
        "python",
        "sql",
        "aws",
        "docker",
        "kubernetes",
        "machine learning",
        "stakeholder management",
    ]

    jd_lower = jd_text.lower()
    for kw in keywords:
        if kw in jd_lower and kw not in existing_skills:
            suggestions.append(f"+ Add evidence-backed bullet showing {kw} experience (project, impact, scope).")

    if "lead" in jd_lower:
        suggestions.append("~ Strengthen leadership bullets with measurable outcomes (team size, delivery impact).")
    if "remote" in jd_lower:
        suggestions.append("~ Include location/remote eligibility near header if accurate.")

    if not suggestions:
        suggestions.append("~ Re-order existing bullets so the most relevant accomplishments appear first.")

    return suggestions


def _linkedin_message(parse: JobParseResult) -> str:
    return (
        f"Hi hiring team at {parse.company}, I came across the {parse.title} role and it aligns well "
        "with my background. I’m especially interested in the scope and would love to share a concise "
        "overview of relevant experience. If helpful, I can send tailored highlights for this position."
    )


def run_job_pipeline(
    jd_text: str,
    constraints: Dict[str, Any] | None = None,
    candidate_profile: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """Run parse -> guardrails/score -> draft generation pipeline."""
    parsed = parse_job_description(jd_text)
    decision: GuardrailDecision = evaluate_job(jd_text, constraints)

    if not decision.proceed:
        return {
            "stage": "rejected",
            "parsed": parsed.__dict__,
            "decision": {
                "proceed": decision.proceed,
                "hard_reject_reasons": decision.hard_reject_reasons,
                "low_signal_reasons": decision.low_signal_reasons,
                "scores": decision.scores,
            },
            "rejection_summary": (
                "Job did not pass guardrails: "
                + ", ".join(decision.hard_reject_reasons + decision.low_signal_reasons)
            ).strip(", "),
        }

    return {
        "stage": "drafts_ready",
        "parsed": parsed.__dict__,
        "decision": {
            "proceed": decision.proceed,
            "hard_reject_reasons": decision.hard_reject_reasons,
            "low_signal_reasons": decision.low_signal_reasons,
            "scores": decision.scores,
        },
        "resume_edits": _resume_edits_from_jd(jd_text, candidate_profile),
        "linkedin_message": _linkedin_message(parsed),
        "rationale": (
            "Proceeding because guardrail checks passed with acceptable fit, role quality, "
            "and company signal scores. Drafts are suggestions only and require human review."
        ),
    }
