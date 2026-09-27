"""
Shared helper: split a resume / job description into labeled sections
by scanning for header lines (e.g. "Experience", "Required Skills").

This is intentionally simple (line-based heading detection) rather than a
layout-aware parser, since the input here is plain text pasted by the user.
"""

import re
from .text_cleaning import split_lines


def _is_heading(line: str, candidates: list[str]) -> bool:
    stripped = line.strip().strip(":").lower()
    if len(stripped) > 40:
        return False
    for c in candidates:
        if stripped == c or stripped.startswith(c + " ") or stripped == c.replace(" ", ""):
            return True
    return False


def split_into_sections(text: str, header_map: dict[str, list[str]]) -> dict[str, str]:
    """
    header_map: {section_key: [possible heading phrases, ...]}
    Returns {section_key: joined body text}. Any text before the first
    recognized heading is returned under the key "_preamble".
    """
    lines = split_lines(text)
    sections: dict[str, list[str]] = {"_preamble": []}
    current = "_preamble"

    flat_candidates = [
        (key, phrase) for key, phrases in header_map.items() for phrase in phrases
    ]
    # longest phrases first so "required skills" beats "skills" substring checks
    flat_candidates.sort(key=lambda kp: len(kp[1]), reverse=True)

    for line in lines:
        matched_key = None
        for key, phrase in flat_candidates:
            if _is_heading(line, [phrase]):
                matched_key = key
                break
        if matched_key:
            current = matched_key
            sections.setdefault(current, [])
            continue
        sections.setdefault(current, [])
        sections[current].append(line)

    return {k: "\n".join(v).strip() for k, v in sections.items()}


YEAR_RANGE_RE = re.compile(
    r"(?P<start>(19|20)\d{2})\s*(-|to|–|—)\s*(?P<end>(19|20)\d{2}|present|current|now)",
    re.IGNORECASE,
)

YEARS_OF_EXPERIENCE_RE = re.compile(
    r"(?P<num>\d{1,2}(?:\.\d)?)\+?\s*(?:-\s*\d{1,2}\s*)?years?\s*(?:of\s+)?(?:relevant\s+|professional\s+|work(?:ing)?\s+)?experience",
    re.IGNORECASE,
)
