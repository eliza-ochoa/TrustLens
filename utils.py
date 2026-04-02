"""Utility helpers for TrustLens.

The functions in this file are intentionally small and rule-based so that
students can understand how the analysis works.
"""

from __future__ import annotations

import re
from typing import Dict, List, Set


RISK_PHRASE_PATTERNS: Dict[str, str] = {
    "unsupported_certainty": r"\b(definitely|certainly|clearly|proves|guarantees?|undeniably|without a doubt|always|never)\b",
    "vague_attribution": r"\b(experts say|research shows|studies say|many people believe|it is said|they say|some people say|critics say)\b",
    "citation_marker": r"(\[\d+\]|\([A-Z][A-Za-z]+,\s*\d{4}\)|according to\s+[A-Z])",
}


ABSOLUTE_TERMS = {
    "all",
    "always",
    "everyone",
    "everything",
    "never",
    "no one",
    "none",
    "only",
}


def normalize_whitespace(text: str) -> str:
    """Collapse repeated whitespace into single spaces."""
    return re.sub(r"\s+", " ", text or "").strip()


def split_sentences(text: str) -> List[str]:
    """Split text into rough sentences with a simple regex."""
    clean_text = normalize_whitespace(text)
    if not clean_text:
        return []
    parts = re.split(r"(?<=[.!?])\s+", clean_text)
    return [part.strip() for part in parts if part.strip()]


def extract_risk_phrases(text: str) -> Dict[str, List[str]]:
    """Return matched phrases for each risk category."""
    matches: Dict[str, List[str]] = {}
    for label, pattern in RISK_PHRASE_PATTERNS.items():
        found = re.findall(pattern, text or "", flags=re.IGNORECASE)
        if found:
            matches[label] = sorted({normalize_whitespace(item) for item in found})
    return matches


def approximate_named_entity_count(text: str) -> int:
    """Estimate the number of named entities using capitalization heuristics.

    This is not a real NLP model. It simply looks for title-case or uppercase
    chunks such as "World Health Organization" or "NASA".
    """
    if not text:
        return 0

    pattern = r"\b(?:[A-Z][a-z]+|[A-Z]{2,})(?:\s+(?:[A-Z][a-z]+|[A-Z]{2,}))*\b"
    candidates = re.findall(pattern, text)
    stopwords = {"The", "A", "An", "In", "On", "At", "For", "This", "That"}

    cleaned = {
        candidate.strip()
        for candidate in candidates
        if candidate.strip() not in stopwords and len(candidate.strip()) > 2
    }
    return len(cleaned)


def identify_quantitative_markers(text: str) -> Dict[str, List[str]]:
    """Find numbers, dates, and percentages."""
    numbers = re.findall(r"\b\d+(?:,\d{3})*(?:\.\d+)?\b", text or "")
    percentages = re.findall(r"\b\d+(?:\.\d+)?%\b", text or "")
    dates = re.findall(
        r"\b(?:\d{4}|\d{1,2}/\d{1,2}/\d{2,4}|"
        r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4})\b",
        text or "",
        flags=re.IGNORECASE,
    )
    return {
        "numbers": sorted(set(numbers)),
        "dates": sorted(set(dates)),
        "percentages": sorted(set(percentages)),
    }


def tokenize_keywords(text: str) -> Set[str]:
    """Create a lightweight keyword set for overlap comparisons."""
    words = re.findall(r"\b[a-zA-Z]{4,}\b", (text or "").lower())
    stopwords = {
        "about",
        "after",
        "because",
        "before",
        "being",
        "could",
        "every",
        "general",
        "other",
        "should",
        "their",
        "there",
        "these",
        "those",
        "using",
        "which",
        "would",
        "while",
    }
    return {word for word in words if word not in stopwords}


def compare_answer_to_source(answer: str, source_text: str) -> Dict[str, object]:
    """Compare the answer with the optional source text using simple overlap rules."""
    if not answer or not source_text:
        return {
            "overlap_ratio": 0.0,
            "shared_keywords": [],
            "missing_numbers": [],
            "missing_dates": [],
            "missing_percentages": [],
        }

    answer_keywords = tokenize_keywords(answer)
    source_keywords = tokenize_keywords(source_text)
    shared_keywords = sorted(answer_keywords & source_keywords)

    overlap_ratio = 0.0
    if answer_keywords:
        overlap_ratio = len(shared_keywords) / len(answer_keywords)

    answer_markers = identify_quantitative_markers(answer)
    source_markers = identify_quantitative_markers(source_text)

    return {
        "overlap_ratio": round(overlap_ratio, 2),
        "shared_keywords": shared_keywords[:12],
        "missing_numbers": sorted(set(answer_markers["numbers"]) - set(source_markers["numbers"])),
        "missing_dates": sorted(set(answer_markers["dates"]) - set(source_markers["dates"])),
        "missing_percentages": sorted(
            set(answer_markers["percentages"]) - set(source_markers["percentages"])
        ),
    }


def contains_absolute_language(text: str) -> bool:
    """Check whether the text uses broad all-or-nothing language."""
    lower_text = (text or "").lower()
    return any(re.search(rf"\b{re.escape(term)}\b", lower_text) for term in ABSOLUTE_TERMS)
