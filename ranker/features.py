"""Feature extraction for all 7 scoring dimensions."""

import math
import re
from datetime import date, datetime
from .config import (
    MUST_HAVE_SKILLS, STRONG_SIGNAL_SKILLS, SUPPORTING_SKILLS,
    SYNONYM_GROUPS, PROFICIENCY_WEIGHTS, TITLE_SCORES, NON_TECH_TITLES,
    CONSULTING_FIRMS, IDEAL_LOCATIONS, TIER1_INDIA_CITIES,
    RETRIEVAL_KEYWORDS, ML_KEYWORDS, PRODUCTION_KEYWORDS, EVAL_KEYWORDS,
    YOE_IDEAL, YOE_SIGMA, EDUCATION_TIER_SCORES, CS_AI_FIELDS,
    REFERENCE_DATE,
)


def _safe_lower(s) -> str:
    return (s or "").lower().strip()


# ---- 1. Skills Features ----

def extract_skills_features(candidate: dict) -> dict:
    skills = candidate.get("skills", [])

    must_have_weighted = 0.0
    strong_signal_weighted = 0.0
    must_have_count = 0
    strong_signal_count = 0
    supporting_count = 0
    python_present = 0.0
    trust_scores = []

    synonym_coverage = {group: False for group in SYNONYM_GROUPS}

    for skill in skills:
        name = skill.get("name", "")
        prof = PROFICIENCY_WEIGHTS.get(skill.get("proficiency", "beginner"), 0.2)
        endorsements = skill.get("endorsements", 0)
        duration = skill.get("duration_months", 0)

        trust = prof * min(1.0, endorsements / 10.0) * min(1.0, (duration or 1) / 24.0)

        for group_name, group_skills in SYNONYM_GROUPS.items():
            if name in group_skills:
                synonym_coverage[group_name] = True

        if name in MUST_HAVE_SKILLS:
            must_have_count += 1
            must_have_weighted += prof * (1 + math.log1p(endorsements)) * min(1.0, (duration or 1) / 24.0)
            trust_scores.append(trust)
        elif name in STRONG_SIGNAL_SKILLS:
            strong_signal_count += 1
            strong_signal_weighted += prof * (1 + math.log1p(endorsements)) * min(1.0, (duration or 1) / 24.0)
        elif name in SUPPORTING_SKILLS:
            supporting_count += 1

        if name == "Python":
            python_present = 1.0

    synonym_bonus = sum(1 for covered in synonym_coverage.values() if covered) / len(SYNONYM_GROUPS)

    max_must_have = len(MUST_HAVE_SKILLS) * 1.0 * (1 + math.log1p(30)) * 1.0
    max_strong = len(STRONG_SIGNAL_SKILLS) * 1.0 * (1 + math.log1p(30)) * 1.0

    return {
        "must_have_count": must_have_count,
        "must_have_weighted": min(1.0, must_have_weighted / max(max_must_have * 0.15, 1)),
        "strong_signal_count": strong_signal_count,
        "strong_signal_weighted": min(1.0, strong_signal_weighted / max(max_strong * 0.10, 1)),
        "supporting_count": supporting_count,
        "python_present": python_present,
        "avg_skill_trust": sum(trust_scores) / max(len(trust_scores), 1),
        "synonym_coverage": synonym_bonus,
    }


# ---- 2. Career Relevance ----

def _count_keyword_hits(text: str, keywords: list[str]) -> int:
    text_lower = text.lower()
    return sum(1 for kw in keywords if kw in text_lower)


def extract_career_features(candidate: dict) -> dict:
    career = candidate.get("career_history", [])
    profile = candidate.get("profile", {})

    all_descriptions = []
    companies_lower = set()
    has_product_exp = False
    total_months_at_consulting = 0
    total_months = 0

    for job in career:
        desc = job.get("description", "") or ""
        all_descriptions.append(desc)
        company = _safe_lower(job.get("company", ""))
        companies_lower.add(company)
        duration = job.get("duration_months", 0) or 0
        total_months += duration

        if company in CONSULTING_FIRMS:
            total_months_at_consulting += duration
        else:
            has_product_exp = True

    combined_text = " ".join(all_descriptions)

    retrieval_hits = _count_keyword_hits(combined_text, RETRIEVAL_KEYWORDS)
    ml_hits = _count_keyword_hits(combined_text, ML_KEYWORDS)
    production_hits = _count_keyword_hits(combined_text, PRODUCTION_KEYWORDS)
    eval_hits = _count_keyword_hits(combined_text, EVAL_KEYWORDS)

    retrieval_score = min(1.0, retrieval_hits / 6.0)
    ml_score = min(1.0, ml_hits / 5.0)
    production_score = min(1.0, production_hits / 4.0)
    eval_score = min(1.0, eval_hits / 3.0)

    career_relevance = (
        0.35 * retrieval_score +
        0.30 * ml_score +
        0.25 * production_score +
        0.10 * eval_score
    )

    consulting_only = (not has_product_exp) and total_months_at_consulting > 0
    consulting_ratio = total_months_at_consulting / max(total_months, 1)

    return {
        "career_relevance": career_relevance,
        "retrieval_score": retrieval_score,
        "ml_score": ml_score,
        "production_score": production_score,
        "eval_score": eval_score,
        "consulting_only": consulting_only,
        "consulting_ratio": consulting_ratio,
        "has_product_exp": has_product_exp,
    }


# ---- 3. Title Relevance ----

def extract_title_features(candidate: dict) -> dict:
    title = candidate.get("profile", {}).get("current_title", "")

    if title in TITLE_SCORES:
        score = TITLE_SCORES[title]
    elif title in NON_TECH_TITLES:
        score = 0.0
    else:
        title_lower = title.lower()
        if any(kw in title_lower for kw in ["ai", "ml", "machine learning", "nlp"]):
            score = 0.85
        elif any(kw in title_lower for kw in ["data", "scientist", "analytics"]):
            score = 0.65
        elif any(kw in title_lower for kw in ["engineer", "developer", "software"]):
            score = 0.45
        elif any(kw in title_lower for kw in ["lead", "architect", "principal"]):
            score = 0.55
        else:
            score = 0.1

    is_non_tech = title in NON_TECH_TITLES or score <= 0.1

    return {
        "title_relevance": score,
        "is_non_tech": is_non_tech,
    }


# ---- 4. Experience (YOE) ----

def extract_yoe_features(candidate: dict) -> dict:
    yoe = candidate.get("profile", {}).get("years_of_experience", 0) or 0.0

    fit = math.exp(-0.5 * ((yoe - YOE_IDEAL) / YOE_SIGMA) ** 2)

    in_range = 1.0 if 4.0 <= yoe <= 10.0 else 0.0

    if yoe < 2.0 or yoe > 15.0:
        penalty = 0.5
    elif yoe < 3.0 or yoe > 12.0:
        penalty = 0.8
    else:
        penalty = 1.0

    return {
        "yoe": yoe,
        "yoe_fit": fit * penalty,
        "yoe_in_range": in_range,
    }


# ---- 5. Location ----

def extract_location_features(candidate: dict) -> dict:
    profile = candidate.get("profile", {})
    signals = candidate.get("redrob_signals", {})

    location = _safe_lower(profile.get("location", ""))
    country = _safe_lower(profile.get("country", ""))
    relocate = signals.get("willing_to_relocate", False)
    work_mode = signals.get("preferred_work_mode", "onsite")

    is_india = country == "india" or any(
        city in location for city in list(IDEAL_LOCATIONS) + list(TIER1_INDIA_CITIES)
    )

    if any(city in location for city in IDEAL_LOCATIONS):
        loc_score = 1.0
    elif any(city in location for city in TIER1_INDIA_CITIES):
        loc_score = 0.9
    elif is_india and relocate:
        loc_score = 0.8
    elif is_india:
        loc_score = 0.6
    elif relocate:
        loc_score = 0.4
    else:
        loc_score = 0.2

    mode_scores = {"hybrid": 1.0, "flexible": 0.9, "onsite": 0.8, "remote": 0.6}
    mode_score = mode_scores.get(work_mode, 0.7)

    return {
        "location_score": loc_score * 0.7 + mode_score * 0.3,
        "is_india": is_india,
    }


# ---- 6. Education ----

def extract_education_features(candidate: dict) -> dict:
    education = candidate.get("education", [])
    if not education:
        return {"education_score": 0.3, "has_cs_ai": False, "has_advanced_degree": False}

    best_tier = 0.3
    has_cs_ai = False
    has_advanced = False

    for edu in education:
        tier = edu.get("tier", "unknown")
        tier_score = EDUCATION_TIER_SCORES.get(tier, 0.3)
        best_tier = max(best_tier, tier_score)

        field = _safe_lower(edu.get("field_of_study", ""))
        if any(f in field for f in CS_AI_FIELDS):
            has_cs_ai = True

        degree = _safe_lower(edu.get("degree", ""))
        if any(d in degree for d in ["m.tech", "m.s.", "m.sc", "ph.d", "mtech", "ms ", "phd"]):
            has_advanced = True

    score = best_tier
    if has_cs_ai:
        score = min(1.0, score + 0.15)
    if has_advanced:
        score = min(1.0, score + 0.10)

    return {
        "education_score": score,
        "has_cs_ai": has_cs_ai,
        "has_advanced_degree": has_advanced,
    }


# ---- 7. Behavioral Signals ----

def _parse_date_safe(s) -> date | None:
    if not s:
        return None
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def extract_behavioral_features(candidate: dict) -> dict:
    signals = candidate.get("redrob_signals", {})

    open_to_work = 1.0 if signals.get("open_to_work_flag", False) else 0.0

    response_rate = signals.get("recruiter_response_rate", 0)
    if response_rate < 0:
        response_rate = 0.0

    response_time = signals.get("avg_response_time_hours", 168)
    response_time_score = max(0.0, 1.0 - response_time / 168.0)

    last_active = _parse_date_safe(signals.get("last_active_date"))
    if last_active:
        days_since = (REFERENCE_DATE - last_active).days
        recency_score = max(0.0, 1.0 - days_since / 180.0)
    else:
        recency_score = 0.0

    interview_rate = signals.get("interview_completion_rate", 0)
    if interview_rate < 0:
        interview_rate = 0.0

    availability = (
        0.20 * open_to_work +
        0.30 * response_rate +
        0.15 * response_time_score +
        0.20 * recency_score +
        0.15 * interview_rate
    )

    profile_complete = signals.get("profile_completeness_score", 0) / 100.0

    github = signals.get("github_activity_score", -1)
    github_score = max(0.0, github / 100.0) if github >= 0 else 0.0

    verified = (
        (1.0 if signals.get("verified_email", False) else 0.0) +
        (1.0 if signals.get("verified_phone", False) else 0.0) +
        (1.0 if signals.get("linkedin_connected", False) else 0.0)
    ) / 3.0

    saved = signals.get("saved_by_recruiters_30d", 0)
    saved_score = min(1.0, saved / 20.0)

    assessments = signals.get("skill_assessment_scores", {})
    if assessments:
        assessment_avg = sum(assessments.values()) / len(assessments) / 100.0
    else:
        assessment_avg = 0.0

    quality = (
        0.25 * profile_complete +
        0.25 * github_score +
        0.20 * verified +
        0.15 * saved_score +
        0.15 * assessment_avg
    )

    notice = signals.get("notice_period_days", 90)
    if notice <= 30:
        notice_score = 1.0
    elif notice <= 60:
        notice_score = 0.8
    elif notice <= 90:
        notice_score = 0.6
    elif notice <= 120:
        notice_score = 0.4
    else:
        notice_score = 0.2

    return {
        "availability": availability,
        "quality": quality,
        "notice_period_score": notice_score,
        "open_to_work": open_to_work,
        "response_rate": response_rate,
        "recency_score": recency_score,
        "github_score": github_score,
    }


# ---- Combined Feature Extraction ----

def extract_all_features(candidate: dict) -> dict:
    features = {}
    features.update(extract_skills_features(candidate))
    features.update(extract_career_features(candidate))
    features.update(extract_title_features(candidate))
    features.update(extract_yoe_features(candidate))
    features.update(extract_location_features(candidate))
    features.update(extract_education_features(candidate))
    features.update(extract_behavioral_features(candidate))
    return features
