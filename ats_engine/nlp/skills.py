from __future__ import annotations
from typing import Set, List, Dict
import json, os
from rapidfuzz import fuzz

_SKILLS = None

def _load_skills() -> List[str]:
    global _SKILLS
    if _SKILLS is not None:
        return _SKILLS
    path = os.path.join(os.path.dirname(__file__), "..", "data", "skills.json")
    path = os.path.abspath(path)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    _SKILLS = sorted(set([s.strip().lower() for s in data.get("skills", []) if s.strip()]))
    return _SKILLS

def extract_skills(text: str, threshold: int = 90) -> Set[str]:
    """Extract skills by matching against a curated dictionary.
    Uses:
    - exact substring matches
    - fuzzy matching for slightly different formatting (e.g. 'powerbi' vs 'power bi')
    """
    if not text:
        return set()
    t = " " + text.lower() + " "
    skills = _load_skills()
    found = set()

    # exact match
    for s in skills:
        if f" {s} " in t:
            found.add(s)

    # fuzzy match for remaining (cheap pass)
    # To keep performance reasonable, only run fuzzy against words up to certain length
    words = list({w.strip() for w in t.split() if 2 < len(w) < 25})
    for s in skills:
        if s in found:
            continue
        # compare with joined variants
        s2 = s.replace(" ", "")
        for w in words:
            if abs(len(w) - len(s2)) > 4:
                continue
            if fuzz.ratio(w.replace(" ", ""), s2) >= threshold:
                found.add(s)
                break
    return found

def recommend_missing_skills(missing_skills: List[str], target_role: str = "") -> List[str]:
    """Simple recommender:
    - return missing skills, prioritized by role hints
    - You can swap this for a learned ranking model later.
    """
    if not missing_skills:
        return []
    role = (target_role or "").lower()
    pri = []
    # very small, explainable heuristics
    for s in missing_skills:
        score = 0
        if "data" in role and s in {"sql","python","pandas","power bi","tableau","excel"}:
            score += 3
        if "ml" in role or "machine learning" in role:
            if s in {"scikit-learn","tensorflow","pytorch","mlflow","huggingface","nlp","spacy"}:
                score += 3
        if "cloud" in role and s in {"aws","azure","gcp","docker","kubernetes","terraform"}:
            score += 2
        pri.append((s, score))
    pri.sort(key=lambda x: x[1], reverse=True)
    return [s for s,_ in pri][:25]
