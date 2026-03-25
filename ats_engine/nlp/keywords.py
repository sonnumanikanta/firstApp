from __future__ import annotations
from typing import List
import re
from sklearn.feature_extraction.text import TfidfVectorizer

# Simple stopwords list (keep it lightweight; spaCy has its own too)
_STOP = set([
    "a","an","the","and","or","to","of","in","for","on","with","as","is","are","was","were",
    "be","been","being","at","by","from","that","this","it","its","their","they","we","you",
    "will","can","may","should","must","have","has","had","do","does","did"
])

_TOKEN_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9\+\#\-\.]{1,}")

def extract_keywords(text: str, top_k: int = 40) -> List[str]:
    """Extract explainable keywords using TF-IDF on ngrams (1-2).
    Because input is a single doc, we 'self-fit' with minimal trick:
    - Fit on [text, text] so TF-IDF behaves consistently
    - Use max_features and ngram_range
    """
    if not text:
        return []
    tokens = _TOKEN_RE.findall(text.lower())
    # quick prune
    joined = " ".join([t for t in tokens if t not in _STOP and len(t) > 2])

    vec = TfidfVectorizer(
        ngram_range=(1,2),
        max_features=800,
        min_df=1,
        stop_words="english",
    )
    X = vec.fit_transform([joined])
    scores = X.toarray()[0]
    feats = vec.get_feature_names_out()
    pairs = sorted(zip(feats, scores), key=lambda x: x[1], reverse=True)
    out = []
    for term, s in pairs:
        term = term.strip()
        if not term:
            continue
        out.append(term)
        if len(out) >= top_k:
            break
    return out
