"""Title taxonomy, job families, query templates and exclusion rules.

The taxonomy is *evidence-driven*: `learned_titles.json` is written back by the
loop whenever a high-scoring job shows up under a title we did not anticipate,
and those titles are folded into the next round of queries.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

LEARNED_PATH = Path(__file__).resolve().parents[2] / "data" / "learned_titles.json"

# --------------------------------------------------------------------------
# Families. `interest` feeds scoring category 3 (subject-matter interest).
# --------------------------------------------------------------------------
FAMILIES: dict[str, dict] = {
    "entertainment_development": {
        "tier": "A",
        "interest": 15,
        "film_relevance": "high",
        "titles": [
            "development assistant", "development coordinator", "development associate",
            "creative development assistant", "creative development coordinator",
            "film development assistant", "tv development assistant",
            "television development coordinator", "scripted development coordinator",
            "unscripted development coordinator", "development researcher",
            "story researcher", "script reader", "story editor assistant",
            "coverage reader", "creative executive assistant", "acquisitions assistant",
            "acquisitions coordinator", "programming assistant", "programming coordinator",
            "content development coordinator", "talent and development coordinator",
            "development executive assistant", "creative affairs coordinator",
            "current programming assistant", "literary assistant", "story analyst",
        ],
        "keywords": [
            "script coverage", "development slate", "pitch materials", "loglines",
            "reads scripts", "creative notes", "writers", "showrunner", "greenlight",
            "ip", "book scouting", "development team",
        ],
    },
    "physical_production": {
        "tier": "A",
        "interest": 13,
        "film_relevance": "high",
        "titles": [
            "production coordinator", "production associate", "production assistant",
            "production office coordinator", "studio production coordinator",
            "production management assistant", "physical production assistant",
            "physical production coordinator", "production operations coordinator",
            "production planning coordinator", "production finance assistant",
            "production finance coordinator", "film budget coordinator",
            "production accountant assistant", "post production coordinator",
            "post-production coordinator", "creative production coordinator",
            "associate producer", "junior producer", "production researcher",
            "production supervisor assistant", "production operations associate",
            "studio operations coordinator", "content operations coordinator",
        ],
        "keywords": [
            "call sheets", "production schedule", "budget actualization", "cost report",
            "crew", "line producer", "shoot", "scheduling", "vendor", "purchase order",
            "production logistics", "studio operations",
        ],
    },
    "ai_creative_production": {
        "tier": "A",
        "interest": 14,
        "film_relevance": "medium",
        "titles": [
            "ai content creator", "generative ai creator", "ai video producer",
            "ai video creator", "ai creative associate", "generative media associate",
            "creative ai specialist", "ai production associate", "ai content producer",
            "synthetic media producer", "ai visual artist", "ai creative producer",
            "creative technology assistant", "generative content specialist",
            "emerging media assistant", "creative innovation associate",
            "creative technologist", "creative tools associate", "ai workflow specialist",
            "ai creative strategist", "generative video artist", "ai motion designer",
            "prompt engineer creative", "ai storyteller", "creative prototyper",
        ],
        "keywords": [
            "midjourney", "runway", "sora", "veo", "kling", "comfyui", "stable diffusion",
            "generative video", "image generation", "text-to-video", "creative prototyping",
            "visual development", "three.js", "webgl", "ai filmmaking",
        ],
    },
    "research_writing": {
        "tier": "B",
        "interest": 11,
        "film_relevance": "low",
        "titles": [
            "research associate", "research assistant", "content researcher",
            "editorial researcher", "media researcher", "entertainment researcher",
            "film researcher", "writer researcher", "content writer",
            "editorial assistant", "research coordinator", "cultural researcher",
            "trend researcher", "creative researcher", "insights associate",
            "insights analyst", "knowledge analyst", "research analyst",
            "archival researcher", "clearance researcher", "fact checker",
        ],
        "keywords": [
            "desk research", "secondary research", "synthesize", "briefs", "reports",
            "trend", "culture", "editorial", "fact-check", "archival",
        ],
    },
    "content_media": {
        "tier": "B",
        "interest": 10,
        "film_relevance": "medium",
        "titles": [
            "content coordinator", "content associate", "editorial coordinator",
            "video content coordinator", "creative content associate",
            "multimedia coordinator", "media coordinator", "content producer",
            "content operations associate", "creative coordinator",
            "junior creative producer", "digital content coordinator",
            "video production coordinator", "programming operations coordinator",
        ],
        "keywords": [
            "content calendar", "video assets", "editorial workflow", "cms",
            "asset management", "publishing", "creative brief",
        ],
    },
    "freedom_professional": {
        "tier": "C",
        "interest": 8,
        "film_relevance": "none",
        "titles": [
            "remote research associate", "remote writer", "project coordinator",
            "program coordinator", "operations coordinator", "content specialist",
            "knowledge management specialist", "research operations coordinator",
            "documentation specialist", "technical writer", "proposal coordinator",
            "grants coordinator", "ai evaluator", "ai trainer", "ai tutor",
            "data annotation specialist", "quality analyst content", "community coordinator",
            "administrative coordinator", "executive coordinator", "program associate",
            "membership coordinator", "events coordinator",
        ],
        "keywords": [
            "remote", "flexible", "autonomy", "asynchronous", "work-life balance",
            "35 hour", "part-time salaried", "four-day week",
        ],
    },
}

TIER_A = [k for k, v in FAMILIES.items() if v["tier"] == "A"]

# --------------------------------------------------------------------------
# Employer-industry universe used by employer discovery.
# --------------------------------------------------------------------------
EMPLOYER_INDUSTRIES = [
    "film studio", "television studio", "streaming service", "production company",
    "independent film company", "production services company", "post-production house",
    "animation studio", "vfx studio", "advertising production company",
    "creative agency", "talent agency", "management company", "casting company",
    "entertainment technology company", "ai media startup", "generative video company",
    "virtual production company", "entertainment research company",
    "film financing company", "distributor", "documentary company",
    "commercial production company", "branded entertainment studio",
    "media nonprofit", "film festival", "public media", "podcast studio",
]

# --------------------------------------------------------------------------
# Query expansion. Cross product of concept pairs + title/location templates.
# --------------------------------------------------------------------------
CONCEPT_PAIRS = [
    "film development", "film coordinator", "television development",
    "production planning", "physical production", "creative production",
    "entertainment research", "studio research", "script development",
    "content development", "AI video", "AI creative", "generative media",
    "creative researcher", "content research", "remote researcher",
    "remote writer", "remote coordinator", "production finance",
    "production operations", "studio operations", "development slate",
    "unscripted development", "documentary research", "archival research",
    "creative technology", "virtual production", "talent development",
]

LOCATION_TERMS = [
    "New York", "NYC", "New York NY", "remote US", "remote New York", "hybrid NYC",
]

ATS_SITE_TERMS = [
    "boards.greenhouse.io", "job-boards.greenhouse.io", "jobs.lever.co",
    "jobs.ashbyhq.com", "apply.workable.com", "jobs.smartrecruiters.com",
    "jobs.jobvite.com", "careers.icims.com", "bamboohr.com/careers",
    "applytojob.com", "teamtailor.com", "recruitee.com", "breezy.hr",
    "comeet.com", "ats.rippling.com", "myworkdayjobs.com", "pinpointhq.com",
]

# --------------------------------------------------------------------------
# Exclusions. A hit here does not auto-reject; it applies a penalty and, for
# HARD_EXCLUDE, drops the job unless lifestyle signals are unusually strong.
# --------------------------------------------------------------------------
LOW_PRIORITY_TITLE_PATTERNS = [
    r"\bfp&a\b", r"\bfinancial analyst\b", r"\baccountant\b", r"\baccounting\b",
    r"\brevenue operations\b", r"\brevops\b", r"\bbanking\b", r"\bcorporate strategy\b",
    r"\bconsultant\b", r"\bconsulting\b", r"\bsales\b", r"\baccount executive\b",
    r"\baccount manager\b", r"\bcustomer success\b", r"\bpaid social\b",
    r"\bperformance marketing\b", r"\bgrowth marketing\b", r"\bsocial media manager\b",
    r"\bmarketing operations\b", r"\bad operations\b", r"\bad ops\b",
    r"\bbusiness intelligence\b", r"\bdata analyst\b", r"\bbusiness analyst\b",
    r"\bcontroller\b", r"\bbookkeep", r"\bunderwrit", r"\bcredit analyst\b",
    r"\brecruiter\b", r"\bsdr\b", r"\bbdr\b", r"\bteller\b",
]

HARD_EXCLUDE_TITLE_PATTERNS = [
    r"\bmanager\b", r"\bdirector\b", r"\bhead of\b", r"\bvp\b", r"\bvice president\b",
    r"\bprincipal\b", r"\bstaff engineer\b", r"\bchief\b", r"\blead\b(?!s? generation)",
    r"\bsenior\b", r"\bsr\.?\b", r"\bexecutive director\b",
]

HARD_EXCLUDE_BODY_PATTERNS = [
    r"unpaid internship", r"this is an unpaid", r"must be currently enrolled",
    r"currently enrolled (?:as|in) a (?:full[- ]time )?(?:student|degree)",
    r"rising (?:junior|senior)", r"for academic credit",
    r"commission[- ]only", r"100% commission", r"1099 only", r"independent contractor only",
]

# --------------------------------------------------------------------------
# Red flags -> (weight, human label). Weight is subtracted from workload score.
# --------------------------------------------------------------------------
RED_FLAGS: dict[str, tuple[float, str]] = {
    r"\bnights and weekends\b|\bnights/weekends\b|\bevenings and weekends\b": (5.0, "nights and weekends required"),
    r"\bweekend(s)? (?:work|availability|shifts?|required)\b": (4.0, "weekend work"),
    r"\bovertime\b(?!\s*(?:is|are)?\s*(?:not|rarely))": (3.0, "overtime expected"),
    r"\bon[- ]call\b": (4.0, "on-call expectations"),
    r"\b(?:50|55|60|70)\+?\s*(?:hours|hrs)\b": (6.0, "50+ hour weeks referenced"),
    r"\b24/7\b|\baround the clock\b": (5.0, "24/7 availability"),
    r"\btravel\b[^.]{0,40}\b(?:25|30|40|50)\s*%": (3.0, "travel 25%+"),
    r"\bhigh[- ]volume\b": (2.0, "high volume workload"),
    r"\bquota\b|\bcommission\b": (4.0, "quota/commission-driven"),
    r"\bmust thrive under pressure\b|\bthrives? under pressure\b": (2.5, "'thrive under pressure'"),
    r"\bwear(?:s|ing)? many hats\b": (2.0, "'wear many hats'"),
    r"\btight deadlines\b|\baggressive deadlines\b": (2.0, "tight deadlines"),
    r"\burgent deliverables\b|\bfire drills\b": (2.0, "urgent deliverables"),
    r"\brotating shifts?\b|\bshift work\b": (4.0, "rotating shifts"),
    r"\bunpredictable (?:schedule|hours)\b|\bhours (?:may )?vary\b": (3.5, "unpredictable schedule"),
    r"\bpersonal assistant\b|\bpersonal errands\b|\bhousehold\b": (5.0, "personal-assistant duties"),
    r"\bmanage(?:s|ing)? (?:complex |busy )?calendars?\b": (2.5, "heavy calendar management"),
    r"\bexpense reports?\b.{0,40}\bcalendar\b": (2.0, "executive support core duty"),
    r"\bfast[- ]paced\b": (1.0, "'fast-paced'"),
    r"\bscrappy\b|\bhustle\b|\broll up your sleeves\b": (1.5, "startup intensity language"),
    r"\bset\b.{0,25}\blong days\b|\b12[- ]hour days\b": (6.0, "long shoot days"),
    r"\bproduction crunch\b|\bcrunch\b": (3.0, "crunch periods"),
    r"\bclient[- ]facing\b.{0,40}\b(?:constant|daily|round)": (2.0, "constant client interaction"),
}

# Positive lifestyle markers -> bonus to workload/acting scores.
GREEN_FLAGS: dict[str, tuple[float, str]] = {
    r"\b(?:30|32|35)\s*(?:hours|hrs)\s*(?:per|a|/)\s*week\b": (5.0, "explicit 30-35h week"),
    r"\bfour[- ]day (?:work )?week\b|\b4[- ]day week\b": (5.0, "4-day week"),
    r"\bflexible (?:schedule|hours|working hours)\b": (3.0, "flexible schedule"),
    r"\bwork[- ]life balance\b": (2.0, "work-life balance stated"),
    r"\bfully remote\b|\b100% remote\b|\bremote[- ]first\b": (3.0, "fully remote"),
    r"\basynchronous\b|\basync[- ]first\b": (2.5, "async culture"),
    r"\bno (?:nights|weekends)\b": (3.0, "no nights/weekends"),
    r"\bunlimited (?:pto|vacation)\b": (1.0, "generous PTO"),
    r"\bhybrid\b.{0,30}\b(?:2|two|3|three) days\b": (2.0, "defined hybrid days"),
    r"\bself[- ]directed\b|\bhigh autonomy\b|\bown your schedule\b": (2.5, "autonomy"),
    r"\bpart[- ]time\b.{0,30}\bsalaried\b": (2.0, "part-time salaried"),
    r"\b35[- ]hour work ?week\b": (5.0, "35-hour week"),
}

EXPERIENCE_RE = re.compile(
    r"(\d{1,2})\s*(?:\+|plus)?\s*(?:-|–|to)?\s*(\d{1,2})?\s*\+?\s*years?"
    r"(?:\s+of)?(?:\s+(?:relevant|related|professional|progressive|industry))?\s+experience",
    re.I,
)

SALARY_RE = re.compile(
    r"\$\s*(\d{2,3})(?:,(\d{3}))?(?:\s*[kK])?\s*(?:-|–|to)\s*\$?\s*(\d{2,3})(?:,(\d{3}))?(?:\s*[kK])?",
)
SALARY_SINGLE_RE = re.compile(r"\$\s*(\d{2,3}),(\d{3})")
HOURLY_RE = re.compile(r"\$\s*(\d{1,3}(?:\.\d{1,2})?)\s*(?:-|–|to|and)?\s*\$?\s*(\d{1,3}(?:\.\d{1,2})?)?\s*(?:per hour|/\s*h(?:ou)?r|an hour|hourly)", re.I)

CLOSED_PATTERNS = [
    r"no longer accepting applications",
    r"this (?:job|position|posting|role) (?:is|has been) (?:closed|filled|expired|removed)",
    r"position (?:has been )?filled",
    r"job (?:expired|no longer available|not found)",
    r"posting (?:is )?no longer (?:active|available)",
    r"we are no longer accepting",
    r"applications (?:are )?closed",
    r"404",
    r"page not found",
    r"this position is no longer open",
    r"oops.{0,20}(?:can.t find|doesn.t exist)",
]


def load_learned_titles() -> list[str]:
    if LEARNED_PATH.exists():
        try:
            return json.loads(LEARNED_PATH.read_text())
        except json.JSONDecodeError:
            return []
    return []


def save_learned_titles(titles: list[str]) -> None:
    LEARNED_PATH.parent.mkdir(parents=True, exist_ok=True)
    LEARNED_PATH.write_text(json.dumps(sorted(set(titles)), indent=2))


def all_titles(include_learned: bool = True) -> list[str]:
    out: list[str] = []
    for fam in FAMILIES.values():
        out.extend(fam["titles"])
    if include_learned:
        out.extend(load_learned_titles())
    return sorted(set(out))


_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _tokens(text: str) -> list[str]:
    return _TOKEN_RE.findall((text or "").lower())


def _phrase_hit(phrase: str, tokens: list[str], token_set: set[str]) -> float:
    """Score a taxonomy phrase against a title's tokens.

    Exact adjacent match scores highest, but "Coordinator, Development" must
    also match the taxonomy entry "development coordinator", so an unordered
    full-token match still counts.
    """
    words = _TOKEN_RE.findall(phrase)
    if not words:
        return 0.0
    joined = " ".join(tokens)
    if " ".join(words) in joined:
        return 3.0 + len(words) * 0.6
    if all(w in token_set for w in words):
        return 2.2 + len(words) * 0.5
    return 0.0


def family_for_title(title: str, description: str = "") -> str:
    """Best-guess family for a posting, by title match then keyword density."""
    tokens = _tokens(title)
    token_set = set(tokens)
    blob_tokens = set(_tokens((title or "") + " " + (description or "")[:8000]))
    blob = " " + " ".join(_tokens((title or "") + " " + (description or "")[:8000])) + " "

    best, best_score = "freedom_professional", 0.0
    for name, fam in FAMILIES.items():
        score = 0.0
        for ttl in fam["titles"]:
            score += _phrase_hit(ttl, tokens, token_set)
        for kw in fam["keywords"]:
            kw_words = _TOKEN_RE.findall(kw)
            if len(kw_words) == 1:
                score += 0.6 if kw_words[0] in blob_tokens else 0.0
            elif " " + " ".join(kw_words) + " " in blob:
                score += 0.8
        if score > best_score:
            best, best_score = name, score
    return best
