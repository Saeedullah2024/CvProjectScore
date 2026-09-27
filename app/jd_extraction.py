"""
Step 3: Job Description Extraction

Pulls structured fields out of a raw job description:
  - required skills
  - preferred skills
  - experience requirements (min years)
  - education requirement (min level)
  - responsibilities
"""

import re

from .text_cleaning import clean_text, flatten_for_matching, split_lines
from .sectionizer import split_into_sections, YEARS_OF_EXPERIENCE_RE
from .cv_extraction import extract_skills, extract_education
from .skills_db import JD_SECTION_HEADERS

MIN_YEARS_RE = re.compile(
    r"(?:minimum|at least|min\.?)\s*(?:of\s*)?(?P<num>\d{1,2})\+?\s*years?",
    re.IGNORECASE,
)


def extract_min_years_required(text: str) -> float:
    flat = flatten_for_matching(text)
    candidates = [float(m.group("num")) for m in MIN_YEARS_RE.finditer(flat)]
    candidates += [float(m.group("num")) for m in YEARS_OF_EXPERIENCE_RE.finditer(flat)]
    return min(candidates) if candidates else 0.0


def extract_responsibilities(resp_section_text: str) -> list[str]:
    if not resp_section_text:
        return []
    lines = split_lines(resp_section_text)
    return [l for l in lines if len(l) > 3][:20]


def extract_jd_profile(raw_jd_text: str) -> dict:
    text = clean_text(raw_jd_text)
    sections = split_into_sections(text, JD_SECTION_HEADERS)

    required_text = sections.get("required", "")
    preferred_text = sections.get("preferred", "")

    # If the JD has no explicit Required/Preferred headings, treat the whole
    # document as "required" so we still get a usable skill list.
    if not required_text and not preferred_text:
        required_text = text

    required_skills = extract_skills(required_text)
    preferred_skills = [s for s in extract_skills(preferred_text) if s not in required_skills]

    education = extract_education("\n".join([sections.get("education", ""), text]))
    min_years = extract_min_years_required(
        "\n".join([sections.get("experience", ""), required_text, text])
    )

    return {
        "raw_length_chars": len(raw_jd_text or ""),
        "required_skills": required_skills,
        "preferred_skills": preferred_skills,
        "experience": {"min_years_required": min_years},
        "education": education,
        "responsibilities": extract_responsibilities(sections.get("responsibilities", "")),
        "sections_detected": [k for k in sections.keys() if k != "_preamble" and sections[k]],
    }
