from __future__ import annotations
from typing import Dict, Tuple, Any
import json, os
from ..nlp.skills import extract_skills
from ..nlp.keywords import extract_keywords

def _load_roles() -> Dict[str, Any]:
    path = os.path.join(os.path.dirname(__file__), "..", "data", "roles.json")
    path = os.path.abspath(path)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def role_match_score(resume: str, jd: str, target_role: str = "") -> Tuple[int, Dict[str, Any]]:
    roles = _load_roles()
    role_name = target_role if target_role in roles else (target_role.title() if target_role.title() in roles else "")
    if not role_name:
        # if no target role, pick best match
        best = ("", 0)
        for r in roles:
            s, _ = role_match_score(resume, jd, r)
            if s > best[1]:
                best = (r, s)
        role_name = best[0] or "Unknown"
        score = best[1]
        return score, {"target_role": role_name, "auto_selected": True, "score": score}

    profile = roles[role_name]
    prof_skills = set([s.lower() for s in profile.get("skills", [])])
    prof_keywords = set([k.lower() for k in profile.get("keywords", [])])

    resume_skills = extract_skills(resume)
    jd_keys = set(extract_keywords(jd, top_k=40))
    resume_keys = set(extract_keywords(resume, top_k=60))

    skills_cov = len(resume_skills.intersection(prof_skills)) / max(len(prof_skills), 1)
    keyword_cov = len(resume_keys.intersection(prof_keywords.union(jd_keys))) / max(len(prof_keywords.union(jd_keys)), 1)

    score = int(round((0.7 * skills_cov + 0.3 * keyword_cov) * 100))
    return score, {
        "target_role": role_name,
        "auto_selected": False,
        "score": score,
        "profile_skills": sorted(list(prof_skills)),
        "matched_profile_skills": sorted(list(resume_skills.intersection(prof_skills))),
    }
