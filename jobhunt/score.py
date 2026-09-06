"""The 100-point scoring model.

Category weights, from the mission brief:
    1. Acting compatibility ....... 30   (most important)
    2. Workload / drain ........... 20
    3. Subject-matter interest .... 15
    4. Compensation / stability ... 15
    5. Accessibility .............. 15
    6. Career optionality .......... 5

Career optionality can never outweigh acting compatibility: it is capped at 5
points and film relevance is deliberately kept out of categories 1 and 2.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, asdict

from .config.candidate import CANDIDATE as C
from .config.taxonomy import (
    FAMILIES, HARD_EXCLUDE_BODY_PATTERNS, HARD_EXCLUDE_TITLE_PATTERNS,
    LOW_PRIORITY_TITLE_PATTERNS,
)
from .normalize import HoursEstimate


@dataclass
class ScoreResult:
    total: float
    acting: float
    workload: float
    interest: float
    comp: float
    access: float
    optionality: float
    penalties: float
    tier: str
    accessibility_label: str
    rationale: list[str]

    def as_dict(self) -> dict:
        return asdict(self)


# ------------------------------------------------------- 1. acting (30) ---
def score_acting(remote_status: str, hours: HoursEstimate, red_flags: list[str],
                 green_flags: list[str], family: str, employment_type: str) -> tuple[float, list[str]]:
    pts, why = 0.0, []

    # Arrangement / geographic freedom (0-10)
    arrangement = {"remote": 10.0, "hybrid": 7.5, "onsite": 3.5, "unknown": 4.5}[remote_status]
    pts += arrangement
    why.append(f"arrangement={remote_status} (+{arrangement:.1f}/10)")

    # Predictability & daytime-audition feasibility (0-10)
    mid = hours.midpoint
    if mid <= 33:
        pred = 10.0
    elif mid <= 37:
        pred = 8.5
    elif mid <= 41:
        pred = 6.5
    elif mid <= 45:
        pred = 4.0
    elif mid <= 50:
        pred = 2.0
    else:
        pred = 0.0
    pts += pred
    why.append(f"~{hours.text} → predictability +{pred:.1f}/10")

    # After-hours / evening-class compatibility (0-10)
    ah = 10.0
    unpredictable = {"nights and weekends required", "weekend work", "on-call expectations",
                     "rotating shifts", "unpredictable schedule", "24/7 availability",
                     "long shoot days", "50+ hour weeks referenced"}
    for f in red_flags:
        if f in unpredictable:
            ah -= 3.0
        elif f in {"overtime expected", "crunch periods", "personal-assistant duties"}:
            ah -= 2.0
        else:
            ah -= 0.6
    for g in green_flags:
        if g in {"flexible schedule", "no nights/weekends", "async culture", "autonomy",
                 "4-day week", "explicit 30-35h week", "35-hour week"}:
            ah += 1.2
    if employment_type == "part_time":
        ah += 1.5
    ah = max(0.0, min(10.0, ah))
    pts += ah
    why.append(f"after-hours/class compatibility +{ah:.1f}/10")

    # Weekly hours actually left for acting + fitness, sanity check.
    free = 168 - 56 - mid - 10  # sleep, work, commute/admin
    if free < C.acting_hours_needed + C.fitness_hours_needed:
        pts -= 2.0
        why.append(f"leaves only ~{free:.0f}h/wk discretionary vs "
                   f"{C.acting_hours_needed + C.fitness_hours_needed}h needed (-2.0)")

    return max(0.0, min(30.0, pts)), why


# ----------------------------------------------------- 2. workload (20) ---
def score_workload(hours: HoursEstimate, red_weight: float, green_weight: float) -> tuple[float, list[str]]:
    mid = hours.midpoint
    if mid <= 35:
        base = 20.0
    elif mid <= 38:
        base = 17.0
    elif mid <= 41:
        base = 14.0
    elif mid <= 45:
        base = 9.0
    elif mid <= 50:
        base = 4.5
    elif mid <= 55:
        base = 1.5
    else:
        base = 0.0
    adj = base - min(8.0, red_weight * 0.8) + min(3.0, green_weight * 0.4)
    return max(0.0, min(20.0, adj)), [
        f"hours midpoint {mid:.0f} → base {base:.1f}/20",
        f"red-flag weight {red_weight:.1f}, green-flag weight {green_weight:.1f}",
    ]


# ----------------------------------------------------- 3. interest (15) ---
def score_interest(family: str, blob: str) -> tuple[float, list[str]]:
    base = float(FAMILIES.get(family, {}).get("interest", 8))
    b = (blob or "").lower()
    bonus = 0.0
    if re.search(r"\bscript|screenplay|screenwrit|film|filmmak|cinema|documentar", b):
        bonus += 0.7
    if re.search(r"\bgenerative|\bai video|\bimage generation|\bdiffusion", b):
        bonus += 0.5
    if re.search(r"\bspreadsheet|reconcil|invoice process|data entry\b", b) and family == "freedom_professional":
        bonus -= 1.5
    return max(0.0, min(15.0, base + bonus)), [f"family={family} base {base:.0f}/15, adj {bonus:+.1f}"]


# ------------------------------------------------- 4. compensation (15) ---
def score_comp(smin: int | None, smax: int | None, employment_type: str,
               hours: HoursEstimate) -> tuple[float, list[str]]:
    why = []
    if smin is None and smax is None:
        base = 8.0                       # unknown: neutral, do not punish
        why.append("salary UNKNOWN → neutral 8.0/15")
    else:
        mid = (smin or smax or 0 + (smax or smin or 0)) / 1
        mid = ((smin or smax) + (smax or smin)) / 2
        if mid < 40_000:
            base = 1.0
        elif mid < C.salary_floor:
            base = 4.0
        elif mid < C.salary_target_low:
            base = 8.5
        elif mid <= C.salary_target_high:
            base = 13.0
        elif mid <= 85_000:
            base = 13.5
        else:
            base = 13.0                  # do not overweight high pay
        why.append(f"midpoint ${mid:,.0f} → {base:.1f}/15")
        # High pay bought with long hours is not worth it.
        if mid > C.salary_target_high and hours.midpoint > 45:
            base -= 3.0
            why.append("high pay but >45h/wk (-3.0)")

    # Unstable, gig-shaped income is the thing to avoid while building an
    # acting career on top of a day job, so contract work is penalised well
    # beyond the small bonus a W-2 role earns.
    stability = {"full_time": 2.0, "part_time": 1.0, "contract": -4.5,
                 "internship": -5.0, "unknown": 0.5}[employment_type]
    why.append(f"employment_type={employment_type} ({stability:+.1f})")
    return max(0.0, min(15.0, base + stability)), why


# ------------------------------------------------- 5. accessibility (15) ---
def score_access(years_req: float | None, title: str, blob: str,
                 family: str) -> tuple[float, str, list[str]]:
    t = (title or "").lower()
    why = []
    if years_req is None:
        base, label = 10.0, "plausible"
        why.append("years requirement not stated → 10.0/15")
    elif years_req <= 2:
        base, label = 15.0, "strong"
        why.append(f"{years_req:.0f}+ yrs required → strong fit 15/15")
    elif years_req <= 3:
        base, label = 11.5, "plausible"
        why.append(f"{years_req:.0f}+ yrs → plausible 11.5/15")
    elif years_req <= 4:
        base, label = 7.0, "stretch"
        why.append(f"{years_req:.0f}+ yrs → stretch 7/15")
    else:
        base, label = 1.0, "poor"
        why.append(f"{years_req:.0f}+ yrs → heavy penalty 1/15")

    if re.search(r"\b(assistant|associate|coordinator|junior|entry[- ]level|analyst i\b)", t):
        base += 1.5
        why.append("junior title (+1.5)")

    # Missing film credentials matter for film-side roles.
    if family in {"entertainment_development", "physical_production"}:
        if re.search(r"\b(?:prior|previous)\s+(?:film|television|tv|production|studio|agency)\s+experience"
                     r"\s+(?:is\s+)?(?:required|a must)", (blob or "").lower()):
            base -= 4.0
            label = "stretch" if label == "plausible" else label
            why.append("requires prior film/TV experience (-4.0)")
        elif re.search(r"\b(?:agency|studio|production company) (?:desk|experience) (?:preferred|a plus)",
                       (blob or "").lower()):
            base -= 1.0
            why.append("industry experience preferred (-1.0)")

    return max(0.0, min(15.0, base)), label, why


# --------------------------------------------------- 6. optionality (5) ---
def score_optionality(family: str, blob: str) -> tuple[float, list[str]]:
    b = (blob or "").lower()
    pts = 0.0
    hits = []
    for pat, val, label in [
        (r"\bactors?\b|\btalent\b|\bcasting\b", 1.0, "talent/casting exposure"),
        (r"\bdirectors?\b|\bproducers?\b|\bshowrunner", 1.0, "director/producer exposure"),
        (r"\bscripts?\b|\bscreenplay", 1.0, "script exposure"),
        (r"\bon set\b|\bproduction\b", 0.7, "production exposure"),
        (r"\bgenerative\b|\bcreative technolog", 0.8, "creative-tech exposure"),
        (r"\bfestival\b|\bpremiere\b|\bindustry events\b", 0.5, "industry events"),
    ]:
        if re.search(pat, b):
            pts += val
            hits.append(label)
    return min(5.0, pts), ([", ".join(hits)] if hits else ["no notable industry exposure"])


# -------------------------------------------------------------- penalty ---
def penalties(title: str, blob: str, employment_type: str,
              salary_min: int | None) -> tuple[float, list[str]]:
    t, b = (title or "").lower(), (blob or "").lower()
    p, why = 0.0, []
    for pat in HARD_EXCLUDE_TITLE_PATTERNS:
        if re.search(pat, t):
            p += 25.0
            why.append(f"seniority/management title matched /{pat}/ (-25)")
            break
    for pat in LOW_PRIORITY_TITLE_PATTERNS:
        if re.search(pat, t):
            p += 12.0
            why.append(f"low-priority field title matched /{pat}/ (-12)")
            break
    for pat in HARD_EXCLUDE_BODY_PATTERNS:
        if re.search(pat, b):
            p += 30.0
            why.append(f"disqualifier in body /{pat}/ (-30)")
            break
    if employment_type == "internship" and not re.search(r"\bpaid\b", b):
        p += 15.0
        why.append("internship with no stated pay (-15)")
    if salary_min is not None and salary_min < 40_000:
        p += 8.0
        why.append(f"salary floor ${salary_min:,} below viability (-8)")
    return p, why


def tier_for(score: float, verification: str, employment_type: str) -> str:
    if verification == "DEAD":
        return "REJECT"
    if score >= 75:
        return "APPLY_NOW" if verification == "LIVE_CONFIRMED" else "APPLY_GOOD_FIT"
    if score >= 65:
        return "APPLY_GOOD_FIT"
    if score >= 55:
        return "STRETCH"
    if score >= 40:
        return "RESEARCH_ONLY"
    return "REJECT"


def score_job(job: dict, hours: HoursEstimate, red_flags: list[str], red_weight: float,
              green_flags: list[str], green_weight: float) -> ScoreResult:
    blob = " ".join(filter(None, [job.get("title"), job.get("description"),
                                  job.get("responsibilities"), job.get("qualifications")]))
    family = job.get("family") or "freedom_professional"
    et = job.get("employment_type") or "unknown"

    acting, w1 = score_acting(job.get("remote_status") or "unknown", hours, red_flags,
                              green_flags, family, et)
    work, w2 = score_workload(hours, red_weight, green_weight)
    interest, w3 = score_interest(family, blob)
    comp, w4 = score_comp(job.get("salary_min"), job.get("salary_max"), et, hours)
    access, label, w5 = score_access(job.get("years_required"), job.get("title") or "", blob, family)
    opt, w6 = score_optionality(family, blob)
    pen, w7 = penalties(job.get("title") or "", blob, et, job.get("salary_min"))

    total = max(0.0, acting + work + interest + comp + access + opt - pen)
    return ScoreResult(
        total=round(total, 1), acting=round(acting, 1), workload=round(work, 1),
        interest=round(interest, 1), comp=round(comp, 1), access=round(access, 1),
        optionality=round(opt, 1), penalties=round(pen, 1),
        tier=tier_for(total, job.get("verification_status") or "UNCERTAIN", et),
        accessibility_label=label,
        rationale=w1 + w2 + w3 + w4 + w5 + w6 + w7,
    )
