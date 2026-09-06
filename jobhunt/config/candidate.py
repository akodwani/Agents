"""Candidate profile and life-design constraints.

The next job is a support system for an acting career. Everything in the
scoring model derives from this file, so tuning the search means editing
here rather than editing scorer internals.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class CandidateProfile:
    home_metro: str = "New York City"
    home_state: str = "NY"

    # Compensation
    salary_floor: int = 45_000          # hard-ish floor
    salary_target_low: int = 50_000     # strongly preferred band
    salary_target_high: int = 65_000

    # Schedule
    ideal_hours_low: int = 30
    ideal_hours_high: int = 35
    acceptable_hours_max: int = 40
    hard_penalty_hours: int = 50        # aggressively penalise at/above this

    # Time the candidate must protect each week
    acting_hours_needed: int = 25       # training / auditions / filmmaking
    fitness_hours_needed: int = 12

    years_experience: float = 2.0
    max_years_required_comfortable: int = 3
    max_years_required_stretch: int = 4

    # Background the scorer can credit
    strengths: tuple[str, ...] = (
        "research", "excel", "financial analysis", "budgeting", "forecasting",
        "reporting", "presentation", "project coordination", "sql", "python",
        "data", "advertising operations", "revenue operations", "banking",
        "ai image generation", "ai video generation", "generative media",
        "three.js", "interactive web", "creative production workflows",
    )
    missing_credentials: tuple[str, ...] = (
        "professional film credits", "professional acting credits",
        "vfx credits", "post-production credits",
    )

    # Acceptable work arrangements, best first
    arrangement_preference: tuple[str, ...] = (
        "remote", "hybrid", "onsite",
    )

    # Employable from New York State only
    remote_must_allow: tuple[str, ...] = ("new york", "ny", "us", "united states", "anywhere")

    health_insurance_required: bool = False
    prefers_w2: bool = True

    # Priority hierarchy, highest first. Used in tie-breaks and narrative output.
    life_priorities: tuple[str, ...] = (
        "serious acting training and eventual auditions/bookings",
        "health, fitness, appearance and energy",
        "stable income",
        "filmmaking / creative opportunities",
        "scalable AI/business experimentation",
        "conventional career progression",
    )

    notes: tuple[str, ...] = field(default_factory=lambda: (
        "Wants to leave current job within weeks to 1-3 months.",
        "Lower prestige is completely acceptable.",
        "Career progression is NOT a requirement.",
        "$60K remote / 30-35h / low pressure beats $50K film job / 55h / unpredictable.",
    ))


CANDIDATE = CandidateProfile()
