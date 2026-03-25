import re

_WS = re.compile(r"\s+")
_BULLETS = re.compile(r"^[\s\-•\*\u2022\u25E6\u25AA\u25CF]+", re.MULTILINE)

def normalize_text(text: str) -> str:
    if not text:
        return ""
    # remove bullet glyphs at line start (keep content)
    text = _BULLETS.sub("", text)
    # normalize whitespace
    text = _WS.sub(" ", text)
    return text.strip().lower()
