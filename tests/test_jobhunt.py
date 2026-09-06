"""Unit tests for the job-discovery scoring and normalisation logic."""

from jobhunt.ats import detect_ats
from jobhunt.config.taxonomy import family_for_title
from jobhunt.normalize import (detect_remote, employment_type, estimate_hours,
                               parse_experience, parse_salary, scan_flags)
from jobhunt.pipeline import dedupe_key, valid_application_url
from jobhunt.score import score_job


def _score(title, company, blob, family, **job):
    hours = estimate_hours(title, company, blob, family, job.get("employment_type", ""))
    reds, red_w, greens, green_w = scan_flags(blob)
    job = {"title": title, "company": company, "description": blob, "family": family, **job}
    return score_job(job, hours, reds, red_w, greens, green_w), hours


class TestSalary:
    def test_annual_range(self):
        assert parse_salary("The range is $55,000 - $65,000")[:2] == (55000, 65000)

    def test_hourly_is_annualised(self):
        lo, hi, text = parse_salary("$28.00 - $32.00 per hour")
        assert (lo, hi) == (58240, 66560) and "annualised" in text

    def test_absent(self):
        assert parse_salary("competitive compensation")[2] == "UNKNOWN"


class TestExperience:
    def test_range(self):
        assert parse_experience("1-3 years of relevant experience")[0] == 1.0

    def test_entry_level(self):
        assert parse_experience("This is an entry-level role")[0] == 0.0

    def test_unknown(self):
        assert parse_experience("You will do great work")[0] is None


class TestRemote:
    def test_hybrid_beats_remote_word(self):
        assert detect_remote("New York, NY", "hybrid role, 3 days in office") == "hybrid"

    def test_fully_remote(self):
        assert detect_remote("Remote", "100% remote team") == "remote"

    def test_onsite_default(self):
        assert detect_remote("New York, NY", "in-office 5 days a week") == "onsite"


class TestHours:
    def test_explicit_hours_are_known(self):
        h = estimate_hours("Coordinator", "Museum", "35-hour work week", "freedom_professional")
        assert h.confidence == "KNOWN" and h.low == 35

    def test_set_language_pushes_hours_up(self):
        h = estimate_hours("Production Coordinator", "Indie", "call sheets, shoot days, "
                           "nights and weekends required", "physical_production")
        assert h.midpoint > 50 and h.confidence == "LIKELY"

    def test_inference_is_never_labelled_known(self):
        h = estimate_hours("Research Associate", "Acme", "desk research", "research_writing")
        assert h.confidence in {"LIKELY", "UNCERTAIN"}


class TestScoring:
    def test_remote_35h_research_beats_55h_film_job(self):
        free, _ = _score("Research Associate", "Foundation",
                         "35-hour work week, fully remote, flexible schedule, desk research",
                         "research_writing", remote_status="remote", salary_min=60000,
                         salary_max=60000, employment_type="full_time", years_required=1)
        film, _ = _score("Production Coordinator", "Indie Films",
                         "call sheets, shoot days, nights and weekends required, fast-paced",
                         "physical_production", remote_status="onsite", salary_min=55000,
                         salary_max=55000, employment_type="full_time", years_required=2)
        assert free.total > film.total + 15

    def test_seniority_is_penalised(self):
        res, _ = _score("Senior Director, Development", "Studio", "lead the slate",
                        "entertainment_development", remote_status="hybrid",
                        employment_type="full_time", years_required=8)
        assert res.tier == "REJECT"

    def test_optionality_cannot_outweigh_acting_compatibility(self):
        res, _ = _score("Production Assistant", "Studio",
                        "actors, directors, producers, scripts, on set, festival, premiere, "
                        "nights and weekends required, 60+ hours, unpredictable schedule",
                        "physical_production", remote_status="onsite",
                        employment_type="full_time", years_required=0)
        assert res.optionality <= 5.0 and res.acting < 12

    def test_student_only_posting_is_dropped(self):
        res, _ = _score("Development Intern", "Studio",
                        "must be currently enrolled as a full-time student",
                        "entertainment_development", remote_status="hybrid",
                        employment_type="internship")
        assert res.tier == "REJECT"


class TestPlumbing:
    def test_ats_detection(self):
        assert detect_ats("https://jobs.lever.co/vevo/abc") == ("lever", "vevo")
        assert detect_ats("https://paramount.wd5.myworkdayjobs.com/en-US/Careers")[0] == "workday"

    def test_search_engine_url_is_never_an_application_url(self):
        assert not valid_application_url("https://www.google.com/search?q=jobs")
        assert valid_application_url("https://job-boards.greenhouse.io/a24/jobs/1")

    def test_dedupe_key_ignores_corporate_suffixes(self):
        assert dedupe_key("A24 Films, Inc.", "Development Coordinator", "New York, NY") == \
               dedupe_key("A24", "Development Coordinator I", "New York, NY")

    def test_family_matches_reordered_titles(self):
        assert family_for_title("Coordinator, Development",
                                "unscripted development slate") == "entertainment_development"

    def test_contract_language_detected(self):
        assert employment_type("this is a contract-style engagement") == "contract"
