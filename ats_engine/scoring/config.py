# Adjust weights to fit your product's interpretation of "ATS readiness".
WEIGHTS = {
    "similarity": 0.35,          # resume <-> JD semantic/lexical similarity
    "keyword_coverage": 0.25,    # matched JD keywords
    "skills_coverage": 0.20,     # matched skills
    "section_health": 0.10,      # presence of core sections
    "bullet_health": 0.05,       # bullet quality heuristics
    "role_match": 0.05,          # match vs role profiles
}

# Hard rules / penalties
PENALTIES = {
    "very_short_resume": 10,   # if resume < 150 words
    "no_contact_info": 8,
    "no_experience_section": 8,
}

MIN_WORDS = 150
