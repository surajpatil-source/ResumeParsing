"""Generate per-candidate reasoning strings — comparative, not just descriptive.

Goal: a judge reading this column should understand *why this candidate
ranks here relative to the JD's stated bar*, not just see their attributes
restated. Avoids near-duplicate phrasing across candidates by rotating
which signal leads based on what's actually distinctive about each profile.
"""

import hashlib
from .config import MUST_HAVE_SKILLS, STRONG_SIGNAL_SKILLS, IDEAL_LOCATIONS, YOE_IDEAL


def _sanitize_text(s: str) -> str:
    """Replace non-ASCII punctuation that source descriptions sometimes
    contain (em/en dashes, smart quotes) with plain ASCII equivalents.
    Avoids any risk of mojibake if the CSV is opened with a tool that
    doesn't correctly assume UTF-8 (e.g. older Excel default import)."""
    replacements = {
        "\u2014": "--", "\u2013": "-",
        "\u2018": "'", "\u2019": "'",
        "\u201c": '"', "\u201d": '"',
        "\u2026": "...",
    }
    for orig, repl in replacements.items():
        s = s.replace(orig, repl)
    return s


def _pick_highlight_sentence(candidate: dict, seen_snippets: set) -> str:
    """Pull a concrete, non-duplicate detail from career descriptions.

    Iterates ALL jobs (not just most recent) and picks the first sentence
    not already used elsewhere in this ranking run, so identical shared
    descriptions in the synthetic dataset don't produce visibly identical
    reasoning across multiple candidates.
    """
    priority_kw = ["ndcg", "latency", "million", "billion", "p95", "a/b",
                   "production", "scale", "deployed", "throughput", "users"]

    candidates_found = []
    for job in reversed(candidate.get("career_history", [])):
        desc = (job.get("description") or "").strip()
        company = job.get("company", "")
        if not desc:
            continue
        for sentence in [s.strip() for s in desc.split(".") if s.strip()]:
            sl = sentence.lower()
            if any(kw in sl for kw in priority_kw):
                key = hashlib.md5(sentence.encode()).hexdigest()[:10]
                candidates_found.append((key, company, sentence[:90]))

    for key, company, snippet in candidates_found:
        if key not in seen_snippets:
            seen_snippets.add(key)
            return f"at {company}: {_sanitize_text(snippet.lower())}"

    # Fallback: every matching sentence was already used elsewhere — use it
    # anyway but note the company for context rather than dropping detail.
    if candidates_found:
        _, company, snippet = candidates_found[0]
        return f"at {company}: {_sanitize_text(snippet.lower())}"
    return ""


def _skill_overlap_phrase(candidate_skills: set, mh: set, ss: set) -> str:
    """Frame skills as overlap-with-JD-bar, not a flat list."""
    if len(mh) >= 6:
        return f"covers {len(mh)} of the JD's core retrieval/ranking skills directly ({', '.join(sorted(mh)[:3])}, +{len(mh)-3} more)"
    elif len(mh) >= 3:
        return f"solid overlap on JD-critical skills: {', '.join(sorted(mh))}"
    elif mh:
        return f"partial JD-skill overlap ({', '.join(sorted(mh))}), broader ML breadth via {', '.join(sorted(ss)[:2]) if ss else 'general stack'}"
    elif ss:
        return f"adjacent ML/LLM skillset ({', '.join(sorted(ss)[:3])}) but light on the JD's specific retrieval stack"
    else:
        return "limited overlap with the JD's named retrieval/ranking stack"


def generate_reasoning(candidate: dict, features: dict, final_score: float, seen_snippets: set = None) -> str:
    if seen_snippets is None:
        seen_snippets = set()

    profile = candidate.get("profile", {})
    signals = candidate.get("redrob_signals", {})
    parts = []

    title = profile.get("current_title", "Unknown")
    yoe = profile.get("years_of_experience", 0)
    company = profile.get("current_company", "")
    location = profile.get("location", "")
    country = profile.get("country", "")

    yoe_delta = abs(yoe - YOE_IDEAL)
    if yoe_delta <= 1.0:
        yoe_phrase = f"{yoe:.1f} yrs (right at the JD's {YOE_IDEAL:.0f}-yr target)"
    elif yoe < YOE_IDEAL:
        yoe_phrase = f"{yoe:.1f} yrs ({YOE_IDEAL - yoe:.1f} yrs below the JD's target band)"
    else:
        yoe_phrase = f"{yoe:.1f} yrs ({yoe - YOE_IDEAL:.1f} yrs above target, still in range)"

    parts.append(f"{title} at {company}, {yoe_phrase}")

    candidate_skills = {s["name"] for s in candidate.get("skills", [])}
    mh = candidate_skills & MUST_HAVE_SKILLS
    ss = candidate_skills & STRONG_SIGNAL_SKILLS
    parts.append(_skill_overlap_phrase(candidate_skills, mh, ss))

    highlight = _pick_highlight_sentence(candidate, seen_snippets)
    if highlight:
        parts.append(highlight)
    elif features.get("career_relevance", 0) > 0.5:
        parts.append("career history shows consistent retrieval/ML substance across roles")
    elif features.get("production_score", 0) > 0.3:
        parts.append("has hands-on production deployment experience")

    rr = signals.get("recruiter_response_rate", -1)
    open_flag = features.get("open_to_work", 0)
    if open_flag and rr >= 0.6:
        parts.append(f"actively job-seeking and highly responsive ({rr:.0%})")
    elif open_flag:
        parts.append("open to work")
    elif rr >= 0 and rr < 0.3:
        parts.append(f"low engagement signal ({rr:.0%} response rate) — availability is a real risk here")

    loc_lower = location.lower()
    is_ideal_loc = any(c in loc_lower for c in IDEAL_LOCATIONS)
    if is_ideal_loc:
        parts.append(f"based in {location} -- JD's preferred location")
    elif location:
        loc_str = f"{location}, {country}" if country and country.lower() != "india" else location
        parts.append(f"based in {loc_str}")

    if features.get("job_hopper_penalty", 1.0) < 1.0:
        parts.append(f"shorter avg tenure ({features.get('avg_tenure_months', 0):.0f}mo) noted but not disqualifying")

    if features.get("consulting_ratio", 0) > 0.5 and features.get("has_product_exp", False):
        parts.append("mostly consulting background but has verified product-company experience")

    return "; ".join(parts) + "."