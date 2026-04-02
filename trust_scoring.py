"""Deterministic scoring logic for TrustLens."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List

from utils import (
    approximate_named_entity_count,
    compare_answer_to_source,
    contains_absolute_language,
    extract_risk_phrases,
    identify_quantitative_markers,
    normalize_whitespace,
    split_sentences,
)


@dataclass
class AnalysisResult:
    score: int
    badge: str
    flagged_issues: List[str]
    missing_evidence: List[str]
    safer_rewrite: str
    recommendation_summary: str
    explainers: List[str]
    detected_signals: List[str]
    triggered_rules: List[str]
    positive_factors: List[str]
    negative_factors: List[str]
    score_breakdown: List[str]


CONTEXT_NOTES: Dict[str, str] = {
    "Class Assignment": "school work usually needs clear support and careful wording",
    "Research": "research work needs strong sourcing and low speculation",
    "Career / Job Prep": "career advice should avoid overconfident claims",
    "General Use": "general use still benefits from evidence, but the risk is usually lower",
}


def analyze_trust(answer: str, source_text: str = "", context: str = "General Use") -> AnalysisResult:
    """Run a rule-based trust analysis.

    The score starts at 100 and loses points for each triggered rule.
    """
    clean_answer = normalize_whitespace(answer)
    clean_source = normalize_whitespace(source_text)

    if not clean_answer:
        return AnalysisResult(
            score=0,
            badge="Low Trust",
            flagged_issues=["No answer text was provided."],
            missing_evidence=["Paste an AI-generated answer before running analysis."],
            safer_rewrite="Please provide the answer text to review.",
            recommendation_summary="Add the AI answer first, then run the analysis again.",
            explainers=["The tool needs content before it can score trust."],
            detected_signals=["Missing answer text"],
            triggered_rules=["empty_answer"],
            positive_factors=[],
            negative_factors=["No answer was available for review."],
            score_breakdown=["Starting score: 100", "-100 Empty input: no answer text was provided."],
        )

    score = 100
    flagged_issues: List[str] = []
    missing_evidence: List[str] = []
    explainers: List[str] = []
    detected_signals: List[str] = []
    triggered_rules: List[str] = []
    positive_factors: List[str] = []
    negative_factors: List[str] = []
    score_breakdown: List[str] = ["Starting score: 100"]

    risk_matches = extract_risk_phrases(clean_answer)
    metrics = identify_quantitative_markers(clean_answer)
    entity_count = approximate_named_entity_count(clean_answer)
    source_comparison = compare_answer_to_source(clean_answer, clean_source)
    sentence_count = len(split_sentences(clean_answer))

    citation_pattern = re.compile(r"(\[\d+\]|\([A-Z][A-Za-z]+,\s*\d{4}\)|according to)", re.IGNORECASE)
    has_citation_style = bool(citation_pattern.search(clean_answer))

    if "unsupported_certainty" in risk_matches:
        score -= 15
        detected_signals.append("Unsupported certainty language")
        triggered_rules.append("unsupported_certainty")
        flagged_issues.append(
            f"Unsupported certainty detected: {', '.join(risk_matches['unsupported_certainty'][:3])}."
        )
        missing_evidence.append("Evidence showing why the claim is certain.")
        explainers.append("Absolute confidence words raise risk when the answer does not prove them.")
        negative_factors.append("Confidence wording sounded stronger than the support shown.")
        score_breakdown.append(
            "-15 Unsupported certainty: strong confidence terms appeared without clear proof."
        )

    if "vague_attribution" in risk_matches:
        score -= 12
        detected_signals.append("Vague attribution")
        triggered_rules.append("vague_attribution")
        flagged_issues.append(
            f"Vague attribution found: {', '.join(risk_matches['vague_attribution'][:3])}."
        )
        missing_evidence.append("A specific author, study, organization, or source.")
        explainers.append("Phrases like 'experts say' sound sourced but do not show who the source is.")
        negative_factors.append("The answer referenced unnamed authorities instead of specific sources.")
        score_breakdown.append("-12 Vague attribution: the answer implied sources without naming them.")

    if not clean_source and not has_citation_style:
        score -= 18
        detected_signals.append("Missing source support")
        triggered_rules.append("missing_source_support")
        flagged_issues.append("No source text or clear citation was provided.")
        missing_evidence.append("A source passage, link, or citation to verify the answer.")
        explainers.append("Trust is lower when there is nothing concrete to check the answer against.")
        negative_factors.append("There was no source passage or clear citation to validate the claims.")
        score_breakdown.append("-18 Missing source support: no source text or citation was available.")

    if contains_absolute_language(clean_answer):
        score -= 10
        detected_signals.append("Overgeneralization")
        triggered_rules.append("overgeneralization")
        flagged_issues.append("Overgeneralization detected through all-or-nothing language.")
        missing_evidence.append("Examples, exceptions, or scope limits.")
        explainers.append("Broad statements often need boundaries or examples to stay reliable.")
        negative_factors.append("All-or-nothing wording made the answer sound broader than the evidence.")
        score_breakdown.append("-10 Overgeneralization: the wording used broad all-or-nothing claims.")

    unsupported_specificity = (
        entity_count >= 3
        or len(metrics["numbers"]) + len(metrics["dates"]) + len(metrics["percentages"]) >= 2
    )
    if unsupported_specificity and not clean_source and not has_citation_style:
        score -= 14
        detected_signals.append("Unsupported specifics")
        triggered_rules.append("unsupported_specifics_without_support")
        flagged_issues.append("The answer includes specific details without supporting evidence.")
        missing_evidence.append("Support for names, numbers, dates, or percentages.")
        explainers.append("Specific facts can look persuasive, so they should be backed by a source.")
        negative_factors.append("Specific names, numbers, or dates appeared without support.")
        score_breakdown.append(
            "-14 Unsupported specifics: detailed claims appeared without a source or citation."
        )

    if clean_source:
        detected_signals.append("Source text provided")
        positive_factors.append("A source passage was provided for direct comparison.")
        score_breakdown.append("+0 Source text provided: the answer could be checked against supplied text.")
        if source_comparison["overlap_ratio"] < 0.2:
            score -= 24
            detected_signals.append("Answer-source mismatch")
            triggered_rules.append("answer_source_mismatch_high")
            flagged_issues.append("Possible mismatch: the answer overlaps very little with the source text.")
            missing_evidence.append("Closer alignment between the answer and the provided source.")
            explainers.append("Low keyword overlap suggests the answer may drift beyond the source.")
            negative_factors.append("The answer had very limited overlap with the provided source text.")
            score_breakdown.append("-24 Answer-source mismatch: overlap with the source was very low.")
        elif source_comparison["overlap_ratio"] < 0.4:
            score -= 12
            detected_signals.append("Partial answer-source mismatch")
            triggered_rules.append("answer_source_mismatch_partial")
            flagged_issues.append("Partial mismatch: the answer only loosely matches the source text.")
            missing_evidence.append("More direct support from the source for the main claims.")
            explainers.append("Some ideas match, but enough gaps remain to lower confidence.")
            negative_factors.append("The answer only loosely matched the source text.")
            score_breakdown.append("-12 Partial source mismatch: the answer only loosely matched the source.")
        else:
            positive_factors.append("The answer shared substantial keyword overlap with the source.")
            score_breakdown.append("+0 Strong overlap: the answer aligned reasonably well with the source.")

        unsupported_markers = (
            source_comparison["missing_numbers"]
            + source_comparison["missing_dates"]
            + source_comparison["missing_percentages"]
        )
        if unsupported_markers:
            score -= min(18, 6 * len(unsupported_markers))
            detected_signals.append("Unsupported numbers, dates, or percentages")
            triggered_rules.append("unsupported_quantitative_markers")
            flagged_issues.append(
                "Specific figures appear in the answer but not in the source: "
                + ", ".join(unsupported_markers[:4])
                + "."
            )
            missing_evidence.append("Source support for the quoted numbers, dates, or percentages.")
            explainers.append("When exact figures do not appear in the source, they should be treated carefully.")
            negative_factors.append("Some exact numbers, dates, or percentages did not appear in the source.")
            score_breakdown.append(
                f"-{min(18, 6 * len(unsupported_markers))} Unsupported markers: exact figures in the answer were missing from the source."
            )
        elif metrics["numbers"] or metrics["dates"] or metrics["percentages"]:
            positive_factors.append("The answer's specific figures appeared to be supported by the source text.")
            score_breakdown.append("+0 Quantitative markers aligned: cited figures appeared in the source.")

    if sentence_count == 1 and len(clean_answer.split()) > 28:
        score -= 6
        detected_signals.append("Compressed long sentence")
        triggered_rules.append("compressed_claims")
        flagged_issues.append("The answer packs many claims into one sentence, which makes checking harder.")
        explainers.append("Long compressed claims are harder to verify step by step.")
        negative_factors.append("Several claims were compressed into one long sentence.")
        score_breakdown.append("-6 Compressed claims: a long single sentence made verification harder.")

    score = max(0, min(100, score))

    if score >= 75:
        badge = "High Trust"
    elif score >= 45:
        badge = "Medium Trust"
    else:
        badge = "Low Trust"

    if not flagged_issues:
        flagged_issues.append("No major rule-based issues were detected.")
        explainers.append("The answer avoided the main risk patterns checked by TrustLens.")
        positive_factors.append("No major rule-based risk patterns were triggered.")
        score_breakdown.append("+0 No major issues: the main deterministic checks were passed.")

    if not missing_evidence:
        missing_evidence.append("No urgent evidence gaps were found by the rule-based checks.")
        positive_factors.append("No urgent evidence gaps were found by the rule-based checks.")

    safer_rewrite = build_safer_rewrite(clean_answer, clean_source)
    recommendation_summary = build_recommendation(score, badge, context, bool(clean_source))

    return AnalysisResult(
        score=score,
        badge=badge,
        flagged_issues=dedupe_list(flagged_issues),
        missing_evidence=dedupe_list(missing_evidence),
        safer_rewrite=safer_rewrite,
        recommendation_summary=recommendation_summary,
        explainers=dedupe_list(explainers),
        detected_signals=dedupe_list(detected_signals),
        triggered_rules=dedupe_list(triggered_rules),
        positive_factors=dedupe_list(positive_factors),
        negative_factors=dedupe_list(negative_factors),
        score_breakdown=score_breakdown,
    )


def dedupe_list(items: List[str]) -> List[str]:
    """Keep order while removing duplicates."""
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def build_safer_rewrite(answer: str, source_text: str) -> str:
    """Rewrite the answer with more cautious wording."""
    rewrite = answer
    replacements = {
        r"\bdefinitely\b": "likely",
        r"\bcertainly\b": "likely",
        r"\bclearly\b": "based on the available information",
        r"\bproves\b": "suggests",
        r"\bguarantees?\b": "may support",
        r"\bundeniably\b": "reasonably",
        r"\balways\b": "often",
        r"\bnever\b": "not always",
    }

    for pattern, replacement in replacements.items():
        rewrite = re.sub(pattern, replacement, rewrite, flags=re.IGNORECASE)

    if source_text:
        prefix = "Based on the provided source, "
    else:
        prefix = "Based on the answer alone, this should be treated as a tentative summary: "

    rewrite = rewrite.strip()
    if rewrite and rewrite[-1] not in ".!?":
        rewrite += "."

    return prefix + rewrite if rewrite else prefix + "more evidence is needed."


def build_recommendation(score: int, badge: str, context: str, has_source: bool) -> str:
    """Create a short student-facing recommendation."""
    context_note = CONTEXT_NOTES.get(context, CONTEXT_NOTES["General Use"])

    if badge == "High Trust":
        return (
            f"This answer looks reasonably usable for {context.lower()}, but you should still verify the key facts "
            f"because {context_note}."
        )
    if badge == "Medium Trust":
        source_note = "Match it against the source before submitting." if has_source else "Add a source before relying on it."
        return f"This answer is usable only with caution. {source_note} The current wording is not strong enough to trust at face value."
    return (
        f"This answer is not reliable enough to use as-is. Rewrite it with weaker claims and add evidence because "
        f"{context_note}."
    )
