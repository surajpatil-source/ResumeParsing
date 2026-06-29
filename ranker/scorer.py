"""Composite scoring: combines feature scores into final rank score."""

from .config import (
    FIT_WEIGHTS, SKILLS_SUB_WEIGHTS, BEHAVIORAL_WEIGHTS,
)


def compute_skills_score(features: dict) -> float:
    return (
        SKILLS_SUB_WEIGHTS["must_have"] * features["must_have_weighted"] +
        SKILLS_SUB_WEIGHTS["strong_signal"] * features["strong_signal_weighted"] +
        SKILLS_SUB_WEIGHTS["python"] * features["python_present"] +
        SKILLS_SUB_WEIGHTS["trust"] * features["avg_skill_trust"]
    )


def compute_fit_score(features: dict, semantic_sim: float = 0.0) -> float:
    skills_score = compute_skills_score(features)

    return (
        FIT_WEIGHTS["skills"] * skills_score +
        FIT_WEIGHTS["career"] * features["career_relevance"] +
        FIT_WEIGHTS["title"] * features["title_relevance"] +
        FIT_WEIGHTS["semantic"] * semantic_sim +
        FIT_WEIGHTS["yoe"] * features["yoe_fit"] +
        FIT_WEIGHTS["location"] * features["location_score"] +
        FIT_WEIGHTS["education"] * features["education_score"]
    )


def compute_behavioral_modifier(features: dict) -> float:
    raw = (
        BEHAVIORAL_WEIGHTS["availability"] * features["availability"] +
        BEHAVIORAL_WEIGHTS["quality"] * features["quality"] +
        BEHAVIORAL_WEIGHTS["notice_period"] * features["notice_period_score"]
    )
    return 0.80 + 0.25 * raw


def compute_final_score(features: dict, semantic_sim: float = 0.0) -> float:
    fit = compute_fit_score(features, semantic_sim)
    modifier = compute_behavioral_modifier(features)
    return fit * modifier


def should_hard_filter(features: dict, is_honeypot: bool) -> bool:
    if is_honeypot:
        return True

    if features["consulting_only"] and not features["has_product_exp"]:
        return True

    if features["is_non_tech"] and features["career_relevance"] < 0.05:
        return True

    return False
