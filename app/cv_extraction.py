"""
Step 2: CV Information Extraction

Pulls structured fields out of raw resume text:
  - skills
  - education (degrees + inferred level)
  - experience (job entries + total years worked)
  - certifications
  - projects
"""

import re
from datetime import datetime

from .text_cleaning import clean_text, flatten_for_matching, split_lines
from .sectionizer import split_into_sections, YEAR_RANGE_RE, YEARS_OF_EXPERIENCE_RE
from .skills_db import (
    ALL_SKILLS, CERTIFICATIONS, DEGREE_LEVELS, DEGREE_PATTERN_KEYWORDS,
    CV_SECTION_HEADERS,
)

THIS_YEAR = datetime.now().year


def extract_skills(full_text: str) -> list[str]:
    flat = flatten_for_matching(full_text)
    found = []
    for skill in ALL_SKILLS:
        pattern = r"(?<![a-z0-9])" + re.escape(skill) + r"(?![a-z0-9])"
        if re.search(pattern, flat):
            found.append(skill)
    # de-dup while keeping longest/most-specific matches (e.g. "react.js" over "react")
    found_sorted = sorted(found, key=len, reverse=True)
    kept: list[str] = []
    for skill in found_sorted:
        if not any(skill != k and skill in k for k in kept):
            kept.append(skill)
    return sorted(kept)


def extract_certifications(full_text: str, section_text: str = "") -> list[str]:
    """
    Known certifications are matched against the whole document (they're
    unambiguous phrases). The generic "certified X" / "X certification"
    pattern is deliberately restricted to the certifications *section* only
    (when one was detected) so it can't run on across unrelated sentences
    once newlines have been flattened to spaces.
    """
    flat_full = flatten_for_matching(full_text)
    found = [c for c in CERTIFICATIONS if c in flat_full]

    if section_text.strip():
        flat_section = flatten_for_matching(section_text)
        for m in re.finditer(r"certified\s+[a-z0-9 \-]{3,40}", flat_section):
            found.append(m.group(0).strip())
        for m in re.finditer(r"[a-z0-9 \-]{3,40}\s+certification", flat_section):
            found.append(m.group(0).strip())

    # dedupe, prefer longer strings
    uniq = sorted(set(found), key=len, reverse=True)
    kept = []
    for c in uniq:
        if not any(c != k and c in k for k in kept):
            kept.append(c)
    return kept[:15]


def extract_education(full_text: str) -> dict:
    flat = flatten_for_matching(full_text)
    degrees_found = []
    for kw in DEGREE_PATTERN_KEYWORDS:
        pattern = r"(?<![a-z0-9])" + re.escape(kw) + r"(?![a-z0-9])"
        if re.search(pattern, flat):
            degrees_found.append(kw)

    highest_level = 0
    highest_label = None
    for d in degrees_found:
        lvl = DEGREE_LEVELS.get(d, 0)
        if lvl > highest_level:
            highest_level = lvl
            highest_label = d

    return {
        "degrees_mentioned": sorted(set(degrees_found), key=len, reverse=True)[:8],
        "highest_level": highest_level,          # 0 = unknown/none detected
        "highest_label": highest_label,
    }


def extract_total_experience_years(full_text: str) -> float:
    """
    Two strategies, take the max:
      1. Explicit phrase like "5+ years of experience"
      2. Sum of (end - start) across detected YYYY-YYYY / YYYY-Present ranges
         in the experience section (overlaps are not de-duplicated; this is
         a heuristic, not payroll-grade calculation).
    """
    flat = flatten_for_matching(full_text)
    explicit_years = [float(m.group("num")) for m in YEARS_OF_EXPERIENCE_RE.finditer(flat)]
    explicit_max = max(explicit_years) if explicit_years else 0.0

    range_years = 0.0
    for m in YEAR_RANGE_RE.finditer(full_text):
        start = int(m.group("start"))
        end_raw = m.group("end").lower()
        end = THIS_YEAR if end_raw in ("present", "current", "now") else int(end_raw)
        if end >= start and (end - start) < 50:
            range_years += (end - start)

    return round(max(explicit_max, range_years), 1)


def extract_job_entries(experience_section_text: str) -> list[dict]:
    """
    Very lightweight heuristic: treats each line containing a year range as
    the anchor of a job entry, and grabs the line above it as a likely
    title/company line.
    """
    lines = split_lines(experience_section_text)
    entries = []
    for i, line in enumerate(lines):
        m = YEAR_RANGE_RE.search(line)
        if m:
            title_line = lines[i - 1] if i > 0 else line
            entries.append({
                "title_or_company_line": title_line.strip(),
                "duration_line": line.strip(),
                "start_year": int(m.group("start")),
                "end_year": (THIS_YEAR if m.group("end").lower() in ("present", "current", "now")
                             else int(m.group("end"))),
            })
    return entries


def extract_projects(projects_section_text: str) -> list[str]:
    if not projects_section_text:
        return []
    lines = split_lines(projects_section_text)
    # group lines into project blocks: a new block starts at a short "title-like" line
    projects: list[str] = []
    current: list[str] = []
    for line in lines:
        looks_like_title = len(line) < 70 and not line.endswith(".")
        if looks_like_title and current:
            projects.append(" ".join(current).strip())
            current = [line]
        else:
            current.append(line)
    if current:
        projects.append(" ".join(current).strip())
    return [p for p in projects if p][:10]


def extract_cv_profile(raw_cv_text: str) -> dict:
    text = clean_text(raw_cv_text)
    sections = split_into_sections(text, CV_SECTION_HEADERS)

    skills_source = "\n".join([sections.get("skills", ""), text])  # fall back to full text
    education = extract_education("\n".join([sections.get("education", ""), text]))
    total_years = extract_total_experience_years(text)
    job_entries = extract_job_entries(sections.get("experience", "") or text)

    return {
        "raw_length_chars": len(raw_cv_text or ""),
        "skills": extract_skills(skills_source),
        "education": education,
        "experience": {
            "total_years_estimated": total_years,
            "job_entries": job_entries,
        },
        "certifications": extract_certifications(
            text, section_text=sections.get("certifications", "")
        ),
        "projects": extract_projects(sections.get("projects", "")),
        "summary_text": sections.get("summary", "")[:800],
        "sections_detected": [k for k in sections.keys() if k != "_preamble" and sections[k]],
    }
