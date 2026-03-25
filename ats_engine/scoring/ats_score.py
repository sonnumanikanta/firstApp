from __future__ import annotations
from typing import Dict
from .config import WEIGHTS, PENALTIES, MIN_WORDS

def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))

def compute_ats_scores(
    similarity: float,
    keyword_coverage: float,
    section_health: float,
    bullet_health: float,
    skills_coverage: float,
    role_match: float,
) -> Dict[str, object]:
    similarity = _clamp01(similarity)
    keyword_coverage = _clamp01(keyword_coverage)
    section_health = _clamp01(section_health)
    bullet_health = _clamp01(bullet_health)
    skills_coverage = _clamp01(skills_coverage)
    role_match = _clamp01(role_match)

    raw = (
        WEIGHTS["similarity"] * similarity +
        WEIGHTS["keyword_coverage"] * keyword_coverage +
        WEIGHTS["skills_coverage"] * skills_coverage +
        WEIGHTS["section_health"] * section_health +
        WEIGHTS["bullet_health"] * bullet_health +
        WEIGHTS["role_match"] * role_match
    )

    ats = int(round(raw * 100))

    # Feedback buckets
    feedback = []
    if similarity < 0.35:
        feedback.append("Resume content is not aligned with the job description. Tailor your experience to match the JD.")
    if keyword_coverage < 0.55:
        feedback.append("Add more job-description keywords naturally across Summary, Skills, and Experience bullets.")
    if skills_coverage < 0.60:
        feedback.append("Your skills section is missing several required skills. Add relevant tools/technologies you actually know.")
    if section_health < 0.70:
        feedback.append("Add missing resume sections (e.g., Summary, Skills, Experience, Education, Projects).")
    if bullet_health < 0.60:
        feedback.append("Improve bullet points: start with strong verbs, add impact + numbers, and keep them concise.")
    if role_match < 0.50:
        feedback.append("Your profile matches the target role weakly. Consider emphasizing role-relevant projects and responsibilities.")

    if not feedback:
        feedback.append("Good ATS readiness. Fine-tune keywords and quantify impact for an even stronger score.")

    return {
        "ats_score": max(0, min(100, ats)),
        "keyword_coverage": round(keyword_coverage, 4),
        "skills_coverage": round(skills_coverage, 4),
        "final_feedback": feedback,
    }
