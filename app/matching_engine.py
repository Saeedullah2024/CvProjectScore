"""
Step 4: Matching Engine

Compares the extracted CV profile against the extracted JD profile along
four axes:
  - skill matching        (exact + fuzzy string matching)
  - semantic similarity    (TF-IDF cosine similarity over full text)
  - experience matching    (years worked vs years required)
  - education matching     (degree level worked vs degree level required)
"""

from difflib import SequenceMatcher

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .text_cleaning import flatten_for_matching

FUZZY_THRESHOLD = 0.84  # similarity ratio above which two skill strings are "the same"


def _fuzzy_equal(a: str, b: str) -> bool:
    if a == b:
        return True
    if a in b or b in a:
        return True
    return SequenceMatcher(None, a, b).ratio() >= FUZZY_THRESHOLD


def match_skills(cv_skills: list[str], jd_required: list[str], jd_preferred: list[str]) -> dict:
    matched_required, missing_required = [], []
    for skill in jd_required:
        if any(_fuzzy_equal(skill, cv_skill) for cv_skill in cv_skills):
            matched_required.append(skill)
        else:
            missing_required.append(skill)

    matched_preferred, missing_preferred = [], []
    for skill in jd_preferred:
        if any(_fuzzy_equal(skill, cv_skill) for cv_skill in cv_skills):
            matched_preferred.append(skill)
        else:
            missing_preferred.append(skill)

    extra_skills = [
        s for s in cv_skills
        if not any(_fuzzy_equal(s, req) for req in jd_required + jd_preferred)
    ]

    required_ratio = (len(matched_required) / len(jd_required)) if jd_required else 1.0
    preferred_ratio = (len(matched_preferred) / len(jd_preferred)) if jd_preferred else 1.0
    # required skills matter more than preferred; weight 80/20
    score = required_ratio * 0.8 + preferred_ratio * 0.2

    return {
        "score": round(score * 100, 1),
        "matched_required": matched_required,
        "missing_required": missing_required,
        "matched_preferred": matched_preferred,
        "missing_preferred": missing_preferred,
        "extra_skills": extra_skills[:20],
    }


def semantic_similarity(cv_text: str, jd_text: str) -> dict:
    cv_flat = flatten_for_matching(cv_text)
    jd_flat = flatten_for_matching(jd_text)

    if not cv_flat or not jd_flat:
        return {"score": 0.0}

    try:
        vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), min_df=1)
        matrix = vectorizer.fit_transform([cv_flat, jd_flat])
        sim = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]
    except ValueError:
        sim = 0.0

    return {"score": round(float(sim) * 100, 1)}


def match_experience(cv_years: float, jd_min_years: float) -> dict:
    if jd_min_years <= 0:
        # JD didn't specify a requirement -> don't penalize
        return {"score": 100.0, "cv_years": cv_years, "required_years": jd_min_years, "meets_requirement": True}

    ratio = cv_years / jd_min_years
    score = min(ratio, 1.0) * 100
    # small partial credit even when short, floors at 0
    score = max(score, 0.0)

    return {
        "score": round(score, 1),
        "cv_years": cv_years,
        "required_years": jd_min_years,
        "meets_requirement": cv_years >= jd_min_years,
    }


def match_education(cv_level: int, jd_level: int, cv_label: str | None, jd_label: str | None) -> dict:
    if jd_level <= 0:
        return {"score": 100.0, "cv_level": cv_label, "required_level": jd_label, "meets_requirement": True}

    if cv_level >= jd_level:
        score = 100.0
    elif cv_level == 0:
        score = 20.0  # no education detected in CV at all
    else:
        # one level below = partial credit, further below = less
        gap = jd_level - cv_level
        score = max(60 - (gap - 1) * 30, 0)

    return {
        "score": round(score, 1),
        "cv_level": cv_label,
        "required_level": jd_label,
        "meets_requirement": cv_level >= jd_level,
    }


def match_certifications(cv_certs: list[str]) -> dict:
    """Certifications are a bonus signal, not directly required by most JDs
    in this pipeline, so we just report count-based confidence."""
    score = min(len(cv_certs) * 20, 100)
    return {"score": float(score), "count": len(cv_certs)}


def run_matching_engine(cv_profile: dict, jd_profile: dict, cv_raw: str, jd_raw: str) -> dict:
    skills_result = match_skills(
        cv_profile["skills"], jd_profile["required_skills"], jd_profile["preferred_skills"]
    )
    semantic_result = semantic_similarity(cv_raw, jd_raw)
    experience_result = match_experience(
        cv_profile["experience"]["total_years_estimated"],
        jd_profile["experience"]["min_years_required"],
    )
    education_result = match_education(
        cv_profile["education"]["highest_level"],
        jd_profile["education"]["highest_level"],
        cv_profile["education"]["highest_label"],
        jd_profile["education"]["highest_label"],
    )
    certifications_result = match_certifications(cv_profile["certifications"])

    return {
        "skills": skills_result,
        "semantic_similarity": semantic_result,
        "experience": experience_result,
        "education": education_result,
        "certifications": certifications_result,
    }
