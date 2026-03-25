from __future__ import annotations
from typing import Dict, List
import re

SECTION_PATTERNS = {
    "contact": re.compile(r"(email|phone|linkedin|github)", re.I),
    "summary": re.compile(r"(professional summary|summary|profile)", re.I),
    "skills": re.compile(r"\b(skills|technical skills|core competencies)\b", re.I),
    "experience": re.compile(r"\b(experience|work history|employment)\b", re.I),
    "education": re.compile(r"\b(education|academic)\b", re.I),
    "projects": re.compile(r"\b(projects|project experience)\b", re.I),
    "certifications": re.compile(r"\b(certifications|certificates)\b", re.I),
}

REQUIRED = ["contact","summary","skills","experience","education"]

def section_recommendations(resume_raw: str) -> Dict[str, object]:
    text = resume_raw or ""
    present = {}
    for sec, pat in SECTION_PATTERNS.items():
        present[sec] = bool(pat.search(text))

    missing_required = [s for s in REQUIRED if not present.get(s, False)]
    recs: List[str] = []
    for s in missing_required:
        if s == "contact":
            recs.append("Add clear contact info: phone, email, LinkedIn (and GitHub if relevant).")
        elif s == "summary":
            recs.append("Add a 2–4 line Professional Summary tailored to the job description.")
        elif s == "skills":
            recs.append("Add a Skills section with JD-relevant tools/technologies in grouped categories.")
        elif s == "experience":
            recs.append("Add an Experience section with role-relevant achievements and metrics.")
        elif s == "education":
            recs.append("Add an Education section with degree, university, and graduation year.")
        else:
            recs.append(f"Add a {s.title()} section.")

    # simple health score
    total = len(REQUIRED)
    have = sum(1 for s in REQUIRED if present.get(s, False))
    section_health = have / max(total, 1)

    return {
        "present_sections": present,
        "missing_required_sections": missing_required,
        "section_health_score": round(section_health, 4),
        "recommendations": recs,
    }
