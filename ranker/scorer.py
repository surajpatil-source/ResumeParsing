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

    recency = features.get("recency_score", 0)
    response = features.get("response_rate", 0)
    open_to_work = features.get("open_to_work", 0)

    # Hard ghost: clearly inactive AND unresponsive AND not looking
    is_hard_ghost = (
        recency < 0.05 and
        response < 0.15 and
        open_to_work == 0.0
    )
    # Soft ghost: borderline unavailable (catches near-misses like response=0.16)
    is_soft_ghost = (
        recency < 0.40 and
        response < 0.20 and
        open_to_work == 0.0
    )

    if is_hard_ghost:
        return 0.55 + 0.15 * raw   # floor ~0.55 for worst ghosts
    if is_soft_ghost:
        return 0.70 + 0.20 * raw   # floor ~0.70 for near-ghosts

    return 0.80 + 0.25 * raw


def compute_final_score(features: dict, semantic_sim: float = 0.0) -> float:
    fit = compute_fit_score(features, semantic_sim)
    modifier = compute_behavioral_modifier(features)
    job_hopper_penalty = features.get("job_hopper_penalty", 1.0)
    langchain_trap_penalty = features.get("langchain_trap_penalty", 1.0)
    cv_speech_trap_penalty = features.get("cv_speech_trap_penalty", 1.0)
    closed_source_penalty = features.get("closed_source_penalty", 1.0)
    title_desc_mismatch_penalty = features.get("title_desc_mismatch_penalty", 1.0)
    return (
        fit * modifier * job_hopper_penalty *
        langchain_trap_penalty * cv_speech_trap_penalty * closed_source_penalty *
        title_desc_mismatch_penalty
    )


def should_hard_filter(features: dict, is_honeypot: bool) -> bool:
    if is_honeypot:
        return True

    if features["consulting_only"] and not features["has_product_exp"]:
        return True

    if features["is_non_tech"] and features["career_relevance"] < 0.05:
        return True

    # Pure research/academic: high ML signal but zero production evidence
    if features.get("ml_score", 0) > 0.6 and features.get("production_score", 0) < 0.05:
        return True

    return False