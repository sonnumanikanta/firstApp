from __future__ import annotations
from typing import Dict, List, Set
import re

ACTION_VERBS = {
    "built","developed","designed","implemented","delivered","led","owned","created","optimized",
    "improved","reduced","increased","automated","analyzed","deployed","migrated","integrated",
    "collaborated","managed","trained","tested","monitored","documented"
}
WEAK_STARTS = {"responsible","worked","helped","involved","participated"}

BULLET_RE = re.compile(r"(^\s*[\-•\*\u2022\u25E6\u25AA\u25CF]\s+.+)$", re.MULTILINE)
NUMBER_RE = re.compile(r"(\b\d+\b|%|\$)")

def _split_bullets(resume_raw: str) -> List[str]:
    bullets = [b.strip() for b in BULLET_RE.findall(resume_raw or "")]
    # if no explicit bullets, try line-based heuristics
    if not bullets:
        lines = [l.strip() for l in (resume_raw or "").splitlines() if l.strip()]
        bullets = [l for l in lines if len(l) > 40][:20]
    return bullets[:30]

def bullet_improvements(resume_raw: str, jd_skills: Set[str] | None = None) -> Dict[str, object]:
    jd_skills = jd_skills or set()
    bullets = _split_bullets(resume_raw or "")
    suggestions: List[Dict[str, str]] = []

    good = 0
    for b in bullets:
        b_l = b.lower()
        first_word = re.sub(r"^[^a-zA-Z]*", "", b_l).split(" ", 1)[0] if b_l else ""
        has_action = first_word in ACTION_VERBS
        has_number = bool(NUMBER_RE.search(b))
        too_long = len(b) > 170
        has_skill = any(s in b_l for s in jd_skills)

        issues = []
        if first_word in WEAK_STARTS or not has_action:
            issues.append("Start with a strong action verb (e.g., Built, Implemented, Optimized).")
        if not has_number:
            issues.append("Add measurable impact (%, $, time saved, scale, users).")
        if too_long:
            issues.append("Shorten to 1–2 lines; keep one key impact per bullet.")
        if jd_skills and not has_skill:
            issues.append("Incorporate a relevant JD skill/tool naturally (only if true).")

        if not issues:
            good += 1
        else:
            suggestions.append({
                "original": b,
                "improvements": " ".join(issues)
            })

    health = 0.0
    if bullets:
        health = good / len(bullets)
    return {
        "bullet_health_score": round(health, 4),
        "suggestions": suggestions[:12],
    }
