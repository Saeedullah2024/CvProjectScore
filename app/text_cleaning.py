"""
Step 1: Text Cleaning / Normalization

Takes raw CV / job description text (as pasted, or extracted upstream from
a PDF/DOCX by the frontend) and normalizes it for the extractors below.
We deliberately keep a "raw" and a "clean" version around: extraction
regexes often need original casing and punctuation (e.g. "B.Sc.", "Node.js"),
while similarity/keyword steps prefer a flattened lowercase version.
"""

import re
import unicodedata


BULLET_CHARS = ["•", "◦", "▪", "‣", "·", "●", "–", "—"]


def normalize_unicode(text: str) -> str:
    """Fold curly quotes, non-breaking spaces, etc. into plain ASCII-ish text."""
    text = unicodedata.normalize("NFKD", text)
    replacements = {
        "\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"',
        "\u2013": "-", "\u2014": "-", "\xa0": " ", "\u2022": "-",
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)
    return text


def normalize_whitespace(text: str) -> str:
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    text = re.sub(r" *\n *", "\n", text)
    return text.strip()


def strip_bullets(line: str) -> str:
    line = line.strip()
    for b in BULLET_CHARS:
        if line.startswith(b):
            line = line[len(b):].strip()
    return re.sub(r"^[-*]\s+", "", line)


def clean_text(raw_text: str) -> str:
    """Full normalization pass, preserving line breaks and original casing."""
    if not raw_text:
        return ""
    text = normalize_unicode(raw_text)
    text = normalize_whitespace(text)
    lines = [strip_bullets(l) for l in text.split("\n")]
    return "\n".join(l for l in lines if l != "")


def flatten_for_matching(text: str) -> str:
    """Lowercase, punctuation-light version used for keyword/regex matching."""
    text = clean_text(text).lower()
    text = re.sub(r"[^a-z0-9\.\+\#\s/&-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def split_lines(text: str) -> list[str]:
    return [l for l in clean_text(text).split("\n") if l.strip()]
