"""Consultant agent output generator.

Produces a structured strategy memo with a mandatory Decision Forcer section.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ConsultingInput:
    """Input payload for generating a consulting recommendation."""

    situation: str
    complication: str
    question: str
    alternatives: tuple[str, ...]


_REQUIRED_SECTIONS: tuple[str, ...] = (
    "SCQA",
    "Issue Tree (Prioritized)",
    "Hypotheses + Tests",
    "Recommendation",
    "90-Day Plan",
    "Decision Forcer (Mandatory Final Step)",
)


_DECISION_FORCER_TEMPLATE = """Decision Forcer (Mandatory Final Step)
1) Kill 2 alternatives:
   - Kill: {kill_one}
   - Kill: {kill_two}
2) Pick 1 path with no hedging:
   - Choose: {chosen}
3) Cost of waiting:
   - {cost_of_waiting}
4) Falsifiability (what changes mind):
   - {falsifiability}
5) Milestones (3 max):
   - M1: {m1}
   - M2: {m2}
   - M3: {m3}
"""


def required_sections() -> tuple[str, ...]:
    """Return the expected section titles in order."""

    return _REQUIRED_SECTIONS


def generate_consulting_output(payload: ConsultingInput) -> str:
    """Generate the consultant output with all required sections.

    If fewer than 3 alternatives are provided, placeholders are used so the
    mandatory Decision Forcer still remains structurally complete.
    """

    alternatives = list(payload.alternatives)
    while len(alternatives) < 3:
        alternatives.append(f"Placeholder Option {len(alternatives) + 1}")

    kill_one, kill_two, chosen = alternatives[1], alternatives[2], alternatives[0]

    body = f"""SCQA
- Situation: {payload.situation}
- Complication: {payload.complication}
- Question: {payload.question}
- Answer: Move quickly on a single focused strategy.

Issue Tree (Prioritized)
1) Strategic fit and expected impact
2) Execution feasibility (capability, bandwidth, dependencies)
3) Unit economics and downside risk
4) Organizational adoption and change management

Hypotheses + Tests
- H1: The chosen strategy creates measurable value in 90 days.
  Test: Launch pilot with baseline metrics and a 30-day readout.
- H2: Team can execute without critical bottlenecks.
  Test: Staffing and dependency stress-test in week 1.
- H3: Financial upside exceeds implementation costs.
  Test: Validate leading indicators against target ROI threshold.

Recommendation
- Commit to {chosen} as the primary path and allocate resources immediately.
- Defer non-essential initiatives that do not improve near-term outcomes.

90-Day Plan
- Days 1-30: Finalize scope, owners, metrics, and launch pilot.
- Days 31-60: Scale what works, remove blockers, and review financial signals.
- Days 61-90: Institutionalize operating model and decide scale-up investment.

"""

    decision_forcer = _DECISION_FORCER_TEMPLATE.format(
        kill_one=kill_one,
        kill_two=kill_two,
        chosen=chosen,
        cost_of_waiting="Delay compounds opportunity loss and increases competitor lead.",
        falsifiability=(
            "If pilot fails to hit agreed leading indicators by day 45 and root-cause "
            "analysis shows no credible recovery path, reverse the decision."
        ),
        m1="Week 2: Pilot live with instrumentation and accountable owner.",
        m2="Day 45: Midpoint review against adoption, quality, and ROI proxies.",
        m3="Day 90: Scale/stop decision with signed executive commitment.",
    )

    return body + decision_forcer


if __name__ == "__main__":
    example = ConsultingInput(
        situation="Growth has plateaued over the last two quarters.",
        complication="Resources are fragmented across too many initiatives.",
        question="Which strategy should leadership prioritize now?",
        alternatives=(
            "Concentrate investment in the highest-performing segment",
            "Expand into an adjacent market immediately",
            "Reduce spend evenly across all programs",
        ),
    )
    print(generate_consulting_output(example))
