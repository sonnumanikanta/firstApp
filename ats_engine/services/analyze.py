from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, List, Tuple, Optional

from ..utils.parsing import parse_resume_file
from ..nlp.cleaning import normalize_text
from ..nlp.keywords import extract_keywords
from ..nlp.skills import extract_skills, recommend_missing_skills
from ..nlp.similarity import compute_similarity
from ..scoring.ats_score import compute_ats_scores
from ..recommendations.sections import section_recommendations
from ..recommendations.bullets import bullet_improvements
from ..role_matching.roles import role_match_score

def parse_file_to_text(uploaded_file) -> str:
    return parse_resume_file(uploaded_file)

def analyze_resume_against_jd(resume_text: str, job_description: str, target_role: str = "") -> Dict[str, Any]:
    resume_raw = resume_text or ""
    jd_raw = job_description or ""

    resume = normalize_text(resume_raw)
    jd = normalize_text(jd_raw)

    # keywords: JD keywords + match in resume
    jd_keywords = extract_keywords(jd, top_k=40)
    resume_keywords = extract_keywords(resume, top_k=60)

    matched_keywords = sorted(list(set(jd_keywords).intersection(set(resume_keywords))))
    missing_keywords = sorted(list(set(jd_keywords) - set(resume_keywords)))

    # skills: use curated dictionary + fuzzy match
    jd_skills = extract_skills(jd)
    resume_skills = extract_skills(resume)
    missing_skills = sorted(list(set(jd_skills) - set(resume_skills)))
    recommended_skills = recommend_missing_skills(missing_skills, target_role=target_role)

    # similarity (TF-IDF baseline; optional embeddings)
    sim = compute_similarity(resume, jd)

    # section recs + bullet suggestions
    section_recs = section_recommendations(resume_raw)
    bullet_sugs = bullet_improvements(resume_raw, jd_skills=jd_skills)

    # role matching
    role_score, role_details = role_match_score(resume, jd, target_role=target_role)

    # ATS score
    scores = compute_ats_scores(
        similarity=sim["combined"],
        keyword_coverage=len(matched_keywords) / max(len(jd_keywords), 1),
        section_health=section_recs["section_health_score"],
        bullet_health=bullet_sugs["bullet_health_score"],
        skills_coverage=len(resume_skills.intersection(jd_skills)) / max(len(jd_skills), 1),
        role_match=role_score / 100.0
    )

    result = {
        "scores": {
            "ats_score": scores["ats_score"],
            "job_description_similarity": sim["combined"],
            "tfidf_similarity": sim["tfidf"],
            "embedding_similarity": sim.get("embedding"),
            "keyword_coverage": scores["keyword_coverage"],
            "skills_coverage": scores["skills_coverage"],
            "role_match_score": role_score,
        },
        "keywords": {
            "matched": matched_keywords,
            "missing": missing_keywords,
            "jd_keywords": jd_keywords,
        },
        "skills": {
            "resume_skills": sorted(list(resume_skills)),
            "jd_skills": sorted(list(jd_skills)),
            "missing_skills": missing_skills,
            "recommended_skills": recommended_skills,
        },
        "recommendations": {
            "sections": section_recs["recommendations"],
            "bullets": bullet_sugs["suggestions"],
            "final_feedback": scores["final_feedback"],
        },
        "role_matching": role_details,
        "meta": {
            "engine": "tempy_ats_engine_v1",
            "target_role": target_role,
        }
    }
    return result
