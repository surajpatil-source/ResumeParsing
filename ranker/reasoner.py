"""Generate per-candidate reasoning strings from actual profile data."""

from .config import MUST_HAVE_SKILLS, STRONG_SIGNAL_SKILLS


def _extract_highlight(candidate: dict) -> str:
    """Pull one concrete detail from career descriptions."""
    for job in reversed(candidate.get("career_history", [])):
        desc = (job.get("description") or "").strip()
        company = job.get("company", "")
        if not desc:
            continue
        for kw in ["million", "billion", "latency", "serving", "scale",
                   "real-time", "production", "deployed", "A/B", "NDCG",
                   "search", "RAG", "vector", "embedding", "ranking"]:
            if kw.lower() in desc.lower():
                sentences = [s.strip() for s in desc.split(".") if kw.lower() in s.lower()]
                if sentences:
                    snippet = sentences[0][:80]
                    return f"at {company}: {snippet.lower()}"
    return ""


def generate_reasoning(candidate: dict, features: dict, final_score: float) -> str:
    profile = candidate.get("profile", {})
    signals = candidate.get("redrob_signals", {})
    parts = []

    title = profile.get("current_title", "Unknown")
    yoe = profile.get("years_of_experience", 0)
    company = profile.get("current_company", "")
    parts.append(f"{title} at {company} with {yoe:.1f} yrs exp")

    candidate_skills = {s["name"] for s in candidate.get("skills", [])}
    mh = candidate_skills & MUST_HAVE_SKILLS
    ss = candidate_skills & STRONG_SIGNAL_SKILLS
    if mh:
        parts.append(f"core skills: {', '.join(sorted(mh)[:4])}")
    if ss and not mh:
        parts.append(f"ML skills: {', '.join(sorted(ss)[:3])}")

    highlight = _extract_highlight(candidate)
    if highlight:
        parts.append(highlight)
    elif features.get("career_relevance", 0) > 0.5:
        parts.append("strong retrieval/ML signal in career history")
    elif features.get("production_score", 0) > 0.3:
        parts.append("has production deployment experience")

    rr = signals.get("recruiter_response_rate", -1)
    if rr >= 0:
        if rr >= 0.7:
            parts.append(f"highly responsive ({rr:.0%} response rate)")
        elif rr < 0.3:
            parts.append(f"low responsiveness ({rr:.0%} response rate)")

    if features.get("open_to_work", 0):
        parts.append("actively looking")

    github = signals.get("github_activity_score", -1)
    if github >= 60:
        parts.append(f"active on GitHub (score {github})")

    location = profile.get("location", "")
    country = profile.get("country", "")
    if location:
        loc_str = f"{location}, {country}" if country and country.lower() != "india" else location
        parts.append(f"based in {loc_str}")

    if yoe < 4:
        parts.append("experience below ideal range")
    elif yoe > 10:
        parts.append("experience above ideal range")

    if features.get("consulting_ratio", 0) > 0.5 and features.get("has_product_exp", False):
        parts.append("mostly consulting background but has some product experience")

    return "; ".join(parts) + "."