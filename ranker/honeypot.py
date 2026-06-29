"""Honeypot detection — flags candidates with subtly impossible profiles."""

from datetime import date, datetime
from .config import REFERENCE_DATE


def _parse_date(s: str | None) -> date | None:
    if not s:
        return None
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def _months_between(d1: date, d2: date) -> float:
    return (d2.year - d1.year) * 12 + (d2.month - d1.month) + (d2.day - d1.day) / 30.0


def check_duration_mismatch(candidate: dict) -> float:
    score = 0.0
    for job in candidate.get("career_history", []):
        start = _parse_date(job.get("start_date"))
        end = _parse_date(job.get("end_date"))
        if not start:
            continue
        if end is None:
            actual_end = REFERENCE_DATE
        else:
            actual_end = end

        actual_months = max(0, _months_between(start, actual_end))
        claimed_months = job.get("duration_months", 0)

        if claimed_months > 0 and actual_months > 0:
            if claimed_months > actual_months * 2 and (claimed_months - actual_months) > 6:
                score += 0.4
    return min(score, 1.0)


def check_expert_zero_duration(candidate: dict) -> float:
    count = 0
    for skill in candidate.get("skills", []):
        if skill.get("proficiency") == "expert" and skill.get("duration_months", 0) == 0:
            count += 1
    if count >= 3:
        return 0.8
    if count >= 2:
        return 0.5
    return 0.0


def check_yoe_vs_career_span(candidate: dict) -> float:
    claimed_yoe = candidate.get("profile", {}).get("years_of_experience", 0)
    earliest_start = None
    for job in candidate.get("career_history", []):
        start = _parse_date(job.get("start_date"))
        if start and (earliest_start is None or start < earliest_start):
            earliest_start = start

    if earliest_start is None:
        return 0.0

    career_span_years = _months_between(earliest_start, REFERENCE_DATE) / 12.0
    if career_span_years > 0 and claimed_yoe > career_span_years + 3:
        return 0.6
    return 0.0


def check_start_after_end(candidate: dict) -> float:
    for job in candidate.get("career_history", []):
        start = _parse_date(job.get("start_date"))
        end = _parse_date(job.get("end_date"))
        if start and end and start > end:
            return 0.7
    return 0.0


def check_title_description_mismatch(candidate: dict) -> float:
    non_tech_indicators = {
        "marketing", "seo", "social media", "brand", "content strategy",
        "hr", "recruitment", "payroll", "compliance",
        "accounting", "bookkeeping", "ledger", "tax",
        "sales quota", "cold call", "crm pipeline",
        "graphic design", "photoshop", "illustrator",
        "civil engineering", "structural", "construction",
        "mechanical", "thermodynamics", "manufacturing",
    }
    tech_titles = {
        "engineer", "developer", "scientist", "ml", "ai", "data",
        "machine learning", "nlp", "software", "backend", "devops",
    }

    title = candidate.get("profile", {}).get("current_title", "").lower()
    is_tech_title = any(t in title for t in tech_titles)

    if not is_tech_title:
        return 0.0

    descriptions = []
    for job in candidate.get("career_history", []):
        desc = (job.get("description") or "").lower()
        if desc:
            descriptions.append(desc)

    if not descriptions:
        return 0.0

    all_text = " ".join(descriptions)
    mismatch_count = sum(1 for ind in non_tech_indicators if ind in all_text)

    tech_evidence = sum(1 for kw in ["model", "deploy", "api", "data", "algorithm",
                                      "training", "inference", "pipeline", "code",
                                      "database", "server", "cloud"] if kw in all_text)

    if mismatch_count >= 3 and tech_evidence <= 1:
        return 0.5
    return 0.0


def compute_honeypot_probability(candidate: dict) -> float:
    scores = [
        check_duration_mismatch(candidate),
        check_expert_zero_duration(candidate),
        check_yoe_vs_career_span(candidate),
        check_start_after_end(candidate),
        check_title_description_mismatch(candidate),
    ]
    combined = 0.0
    for s in scores:
        combined = 1.0 - (1.0 - combined) * (1.0 - s)
    return combined


def detect_honeypots(candidates: list[dict], threshold: float = 0.4) -> set[str]:
    flagged = set()
    for c in candidates:
        prob = compute_honeypot_probability(c)
        if prob >= threshold:
            flagged.add(c["candidate_id"])
    return flagged
