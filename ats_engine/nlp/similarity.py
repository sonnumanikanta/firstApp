from __future__ import annotations
from typing import Dict, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def _tfidf_sim(a: str, b: str) -> float:
    vec = TfidfVectorizer(stop_words="english", ngram_range=(1,2), max_features=5000)
    X = vec.fit_transform([a, b])
    sim = cosine_similarity(X[0], X[1])[0][0]
    return float(sim)

def _embedding_sim(a: str, b: str) -> Optional[float]:
    """Optional semantic similarity using sentence-transformers if installed and model available.
    Keeps infra simple: loads a small model once.
    """
    try:
        from sentence_transformers import SentenceTransformer
        from sentence_transformers.util import cos_sim
    except Exception:
        return None

    try:
        # small, fast model; you can change this in settings
        model = SentenceTransformer("all-MiniLM-L6-v2")
        embs = model.encode([a, b], normalize_embeddings=True)
        sim = float(cos_sim(embs[0], embs[1]).item())
        # cos_sim can be [-1,1], clamp to [0,1]
        sim = max(0.0, min(1.0, (sim + 1.0) / 2.0))
        return sim
    except Exception:
        return None

def compute_similarity(resume: str, jd: str) -> Dict[str, float]:
    tfidf = _tfidf_sim(resume, jd)
    emb = _embedding_sim(resume, jd)

    if emb is None:
        combined = tfidf
    else:
        # Weighted blend; TF-IDF is more "ATS-like" keyword-driven
        combined = 0.65 * tfidf + 0.35 * emb

    return {
        "tfidf": round(tfidf, 4),
        "embedding": None if emb is None else round(emb, 4),
        "combined": round(float(combined), 4),
    }
