"""Field normalisation and conservative inference from posting text.

Everything here is explicit about confidence. An inferred 35-hour week is
never recorded as KNOWN.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field

from .config.taxonomy import (
    EXPERIENCE_RE, GREEN_FLAGS, HOURLY_RE, RED_FLAGS, SALARY_RE,
    SALARY_SINGLE_RE, FAMILIES, family_for_title,
)

WS = re.compile(r"\s+")


def clean(text: str | None) -> str:
    return WS.sub(" ", (text or "")).strip()


def norm_title(title: str) -> str:
    t = (title or "").lower()
    t = re.sub(r"\(.*?\)", " ", t)
    t = re.sub(r"[^a-z0-9 ]+", " ", t)
    t = re.sub(r"\b(i{1,3}|iv|v|jr|sr|1|2|3)\b", " ", t)
    stop = {"the", "a", "an", "of", "and", "for", "to", "at", "in", "&"}
    words = [w for w in t.split() if w not in stop]
    return " ".join(words)


def norm_company(name: str) -> str:
    n = (name or "").lower()
    n = re.sub(r"[^a-z0-9 ]+", " ", n)
    n = re.sub(r"\b(inc|llc|ltd|lp|plc|corp|corporation|co|company|group|studios?|media|"
               r"entertainment|productions?|pictures|films?|networks?|holdings|"
               r"international|worldwide|the)\b", " ", n)
    return WS.sub(" ", n).strip()


def norm_location(loc: str) -> str:
    l = (loc or "").lower()
    if not l:
        return "unknown"
    if re.search(r"\bremote\b|\banywhere\b|\bwork from home\b", l) and not re.search(r"hybrid", l):
        return "remote"
    if re.search(r"\bnew york\b|\bnyc\b|\bmanhattan\b|\bbrooklyn\b|\bny, ny\b|\bnew york, ny\b", l):
        return "new york, ny"
    return WS.sub(" ", re.sub(r"[^a-z0-9, ]+", " ", l)).strip()


def content_hash(*parts: str) -> str:
    return hashlib.sha256("||".join(clean(p) for p in parts).encode()).hexdigest()[:32]


# ---------------------------------------------------------------- remote ---
def detect_remote(location: str, blob: str) -> str:
    l, b = (location or "").lower(), (blob or "").lower()[:6000]
    text = l + " " + b
    hybrid = re.search(r"\bhybrid\b|\b(?:2|3|two|three) days (?:per week )?in (?:the )?office\b", text)
    fully = re.search(r"\bfully remote\b|\b100% remote\b|\bremote[- ]first\b|\bwork from anywhere\b", text)
    remote_word = re.search(r"\bremote\b|\btelecommut", text)
    onsite = re.search(r"\bon[- ]?site\b|\bin[- ]office\b|\b5 days (?:a|per) week in\b|\bin[- ]person\b", text)
    if fully and not hybrid:
        return "remote"
    if hybrid:
        return "hybrid"
    if remote_word and not onsite:
        return "remote"
    if onsite or l.strip():
        return "onsite"
    return "unknown"


def remote_employable_from_ny(blob: str) -> bool | None:
    """None = unknown. False = posting restricts remote work to other states."""
    b = (blob or "").lower()
    if re.search(r"\b(?:new york|ny)\b", b) and re.search(r"remote", b):
        return True
    m = re.search(r"remote[^.]{0,120}?(?:residents? of|located in|based in|eligible in)\s*([^.]{0,160})", b)
    if m:
        states = m.group(1)
        return bool(re.search(r"\bnew york\b|\bny\b|\ball (?:50 )?states\b|\banywhere in the u", states))
    return None


# ---------------------------------------------------------------- salary ---
def parse_salary(blob: str) -> tuple[int | None, int | None, str]:
    b = blob or ""
    m = SALARY_RE.search(b)
    if m:
        lo = _money(m.group(1), m.group(2))
        hi = _money(m.group(3), m.group(4))
        if lo and hi and lo <= hi and lo >= 20_000:
            return lo, hi, clean(m.group(0))
    m = HOURLY_RE.search(b)
    if m:
        lo = float(m.group(1))
        hi = float(m.group(2)) if m.group(2) else lo
        if 12 <= lo <= 200:
            return int(lo * 2080), int(hi * 2080), clean(m.group(0)) + " (annualised @2080h)"
    hits = [_money(g1, g2) for g1, g2 in SALARY_SINGLE_RE.findall(b)]
    hits = [h for h in hits if h and 20_000 <= h <= 400_000]
    if hits:
        return min(hits), max(hits), f"${min(hits):,}" + (f" - ${max(hits):,}" if max(hits) != min(hits) else "")
    return None, None, "UNKNOWN"


def _money(g1: str, g2: str | None) -> int | None:
    if not g1:
        return None
    n = int(g1)
    if g2:
        return n * 1000 + int(g2)
    return n * 1000 if n < 500 else n


# ------------------------------------------------------------ experience ---
def parse_experience(blob: str) -> tuple[float | None, str]:
    best: float | None = None
    raw = "UNKNOWN"
    for m in EXPERIENCE_RE.finditer(blob or ""):
        lo = float(m.group(1))
        if lo > 25:
            continue
        if best is None or lo < best:
            best, raw = lo, clean(m.group(0))
    if best is None and re.search(r"\bentry[- ]level\b|\bno experience (?:required|necessary)\b|\b0-1 years?\b",
                                  (blob or "").lower()):
        return 0.0, "entry-level"
    return best, raw


# ----------------------------------------------------------------- flags ---
def scan_flags(blob: str) -> tuple[list[str], float, list[str], float]:
    b = (blob or "").lower()
    reds, red_w, greens, green_w = [], 0.0, [], 0.0
    for pat, (w, label) in RED_FLAGS.items():
        if re.search(pat, b):
            reds.append(label)
            red_w += w
    for pat, (w, label) in GREEN_FLAGS.items():
        if re.search(pat, b):
            greens.append(label)
            green_w += w
    return reds, red_w, greens, green_w


# ----------------------------------------------------------------- hours ---
# Base weekly-hour priors by family + employer type. Deliberately conservative.
FAMILY_HOUR_PRIOR = {
    "entertainment_development": (40, 48),
    "physical_production": (44, 54),
    "ai_creative_production": (40, 48),
    "research_writing": (38, 42),
    "content_media": (40, 45),
    "freedom_professional": (37, 42),
}

LOW_DRAIN_EMPLOYER_HINTS = re.compile(
    r"\b(?:university|college|museum|library|foundation|nonprofit|non-profit|"
    r"public media|institute|archive|association|society|government|city of|state of)\b", re.I)

SET_WORK_RE = re.compile(
    r"\\b(?:on set|on-set|call sheet|call time|shoot day|principal photography|"
    r"location scout|crew call|wrap|day player|film set|production office on location)\\b", re.I)

HIGH_DRAIN_EMPLOYER_HINTS = re.compile(
    r"\b(?:agency|startup|seed[- ]stage|series a|hedge fund|trading|consultanc)\b", re.I)


@dataclass
class HoursEstimate:
    low: int
    high: int
    confidence: str          # KNOWN | LIKELY | UNCERTAIN
    basis: list[str] = field(default_factory=list)

    @property
    def text(self) -> str:
        return f"{self.low}-{self.high} h/wk" if self.low != self.high else f"{self.low} h/wk"

    @property
    def midpoint(self) -> float:
        return (self.low + self.high) / 2


def estimate_hours(title: str, company: str, blob: str, family: str,
                   employment_type: str = "") -> HoursEstimate:
    b = (blob or "").lower()
    basis: list[str] = []

    m = re.search(r"\b(\d{2})(?:\s*(?:-|–|to)\s*(\d{2}))?\s*(?:hours|hrs)\s*(?:per|a|/)\s*week\b", b)
    if m:
        lo = int(m.group(1))
        hi = int(m.group(2)) if m.group(2) else lo
        return HoursEstimate(lo, hi, "KNOWN", ["explicit hours in posting"])
    if re.search(r"\b35[- ]hour work ?week\b", b):
        return HoursEstimate(35, 35, "KNOWN", ["explicit 35-hour work week"])
    if re.search(r"\bfour[- ]day (?:work )?week\b|\b4[- ]day (?:work )?week\b", b):
        return HoursEstimate(32, 36, "KNOWN", ["four-day week stated"])

    lo, hi = FAMILY_HOUR_PRIOR.get(family, (40, 45))
    basis.append(f"{family} prior")

    if family == "physical_production" and not SET_WORK_RE.search(b):
        # Office-based production coordination (network marketing, post ops,
        # brand studios) is a very different job from working on set.
        lo, hi = 41, 48
        basis[-1] = "physical_production prior, office-based (no on-set language)"

    if employment_type == "part_time":
        lo, hi = min(lo, 20), min(hi, 30)
        basis.append("part-time")

    if re.search(r"\bnon[- ]exempt\b|\bhourly\b|\bovertime eligible\b", b):
        lo, hi = lo - 3, hi - 4
        basis.append("non-exempt/hourly (overtime is paid & tracked)")
    if re.search(r"\bexempt\b(?!\s*from)", b):
        hi += 2
        basis.append("exempt (uncapped hours)")

    if LOW_DRAIN_EMPLOYER_HINTS.search(company or "") or LOW_DRAIN_EMPLOYER_HINTS.search(b[:2000]):
        lo, hi = lo - 4, hi - 6
        basis.append("institutional/nonprofit employer")
    if HIGH_DRAIN_EMPLOYER_HINTS.search(company or ""):
        hi += 3
        basis.append("agency/startup employer")

    reds, red_w, greens, green_w = scan_flags(blob)
    if red_w:
        hi += min(12, red_w)
        lo += min(6, red_w / 2)
        basis.append(f"red flags (+{min(12, red_w):.0f}h): {', '.join(reds[:4])}")
    if green_w:
        hi -= min(8, green_w)
        lo -= min(5, green_w / 2)
        basis.append(f"green flags: {', '.join(greens[:4])}")

    if re.search(r"\bset\b|\bon location\b|\bcall time\b|\bshoot days?\b", b) and family == "physical_production":
        lo, hi = lo + 4, hi + 8
        basis.append("on-set / call-time language")

    lo = max(15, int(round(lo)))
    hi = max(lo + 2, int(round(hi)))
    confidence = "LIKELY" if (red_w or green_w or employment_type == "part_time") else "UNCERTAIN"
    return HoursEstimate(lo, hi, confidence, basis)


def drain_estimate(hours: HoursEstimate, red_w: float, family: str) -> str:
    m = hours.midpoint
    if m <= 36 and red_w < 3:
        return "low"
    if m <= 43 and red_w < 7:
        return "moderate"
    if m <= 50:
        return "high"
    return "severe"


def employment_type(blob: str, given: str = "") -> str:
    g = (given or "").lower()
    if "part" in g:
        return "part_time"
    if "intern" in g:
        return "internship"
    if "contract" in g or "temp" in g or "freelance" in g:
        return "contract"
    if "full" in g:
        return "full_time"
    b = (blob or "").lower()
    if re.search(r"\bpart[- ]time\b", b):
        return "part_time"
    if re.search(r"\binternship\b|\bintern\b(?!al)", b):
        return "internship"
    if re.search(r"\bfreelance\b|\b1099\b|\bcontract(?:[- ](?:role|position|style|based|basis))?\b|"
                 r"\bcontractor\b|\btemporary\b|\btemp\b|\bday ?player\b|\bper[- ]diem\b", b):
        return "contract"
    if re.search(r"\bfull[- ]time\b|\bfte\b|\bstaff position\b", b):
        return "full_time"
    return "unknown"


def classify_family(title: str, description: str) -> tuple[str, str, int]:
    fam = family_for_title(title, description)
    meta = FAMILIES[fam]
    return fam, meta["film_relevance"], meta["interest"]
