"""Streamlit interface for TrustLens."""

from __future__ import annotations

import streamlit as st

from sample_data import SAMPLE_EXAMPLES
from trust_scoring import AnalysisResult, analyze_trust


st.set_page_config(page_title="TrustLens", page_icon="TL", layout="wide")


def apply_styles() -> None:
    """Apply a clean, competition-ready visual style."""
    st.markdown(
        """
        <style>
            :root {
                --bg: #f4f7fb;
                --card: rgba(255, 255, 255, 0.92);
                --line: #d9e2ec;
                --text: #10233a;
                --muted: #587089;
                --teal: #0f766e;
                --navy: #173a5e;
                --high-bg: #e8f7ef;
                --high-text: #166534;
                --medium-bg: #fff5db;
                --medium-text: #92400e;
                --low-bg: #fbe4e6;
                --low-text: #b42318;
            }
            .stApp {
                background:
                    radial-gradient(circle at top left, rgba(15, 118, 110, 0.08), transparent 30%),
                    radial-gradient(circle at top right, rgba(23, 58, 94, 0.08), transparent 25%),
                    var(--bg);
                color: var(--text);
            }
            .block-container {
                max-width: 1180px;
                padding-top: 1.4rem;
                padding-bottom: 2.5rem;
            }
            .hero-card, .panel-card, .metric-card, .comparison-card, .footer-card {
                background: var(--card);
                border: 1px solid var(--line);
                border-radius: 20px;
                padding: 1.1rem 1.2rem;
                box-shadow: 0 18px 45px rgba(15, 23, 42, 0.07);
            }
            .hero-card {
                padding: 1.35rem 1.4rem;
                margin-bottom: 1rem;
            }
            .eyebrow {
                font-size: 0.78rem;
                text-transform: uppercase;
                letter-spacing: 0.12em;
                font-weight: 700;
                color: var(--teal);
                margin-bottom: 0.5rem;
            }
            .hero-title {
                font-size: 2.55rem;
                line-height: 1.05;
                font-weight: 800;
                color: var(--navy);
                margin-bottom: 0.35rem;
            }
            .hero-subtitle {
                margin: 0;
                font-size: 1rem;
                color: var(--muted);
                max-width: 760px;
            }
            .banner {
                background: #eef6ff;
                border: 1px solid #c7d9ee;
                border-radius: 18px;
                padding: 0.95rem 1rem;
                margin-bottom: 1rem;
            }
            .banner-title {
                font-weight: 700;
                color: var(--navy);
                margin-bottom: 0.25rem;
            }
            .banner-copy {
                color: var(--muted);
                margin: 0;
            }
            .section-label {
                font-size: 0.78rem;
                text-transform: uppercase;
                letter-spacing: 0.1em;
                color: var(--muted);
                font-weight: 700;
                margin-bottom: 0.55rem;
            }
            .section-title {
                font-size: 1.15rem;
                font-weight: 700;
                color: var(--navy);
                margin-bottom: 0.2rem;
            }
            .mini-note {
                color: var(--muted);
                font-size: 0.95rem;
                margin: 0;
            }
            .sample-note {
                display: inline-block;
                margin-top: 0.45rem;
                font-size: 0.9rem;
                color: var(--muted);
            }
            .score-value {
                font-size: 4.25rem;
                line-height: 1;
                font-weight: 800;
                color: var(--navy);
                margin-bottom: 0.45rem;
            }
            .score-copy {
                color: var(--muted);
                margin-top: 0.65rem;
                margin-bottom: 0;
            }
            .score-panel {
                background: linear-gradient(180deg, #ffffff, #f4f8fc);
                border: 1px solid #cfdbe7;
                border-radius: 18px;
                padding: 1.2rem 1.2rem 1rem 1.2rem;
            }
            .score-kicker {
                font-size: 0.82rem;
                text-transform: uppercase;
                letter-spacing: 0.12em;
                color: var(--teal);
                font-weight: 700;
                margin-bottom: 0.55rem;
            }
            .trust-badge {
                display: inline-flex;
                align-items: center;
                padding: 0.45rem 0.8rem;
                border-radius: 999px;
                font-weight: 700;
                font-size: 0.95rem;
                border: 1px solid transparent;
            }
            .badge-high {
                background: var(--high-bg);
                color: var(--high-text);
                border-color: #b7e1c5;
            }
            .badge-medium {
                background: var(--medium-bg);
                color: var(--medium-text);
                border-color: #f3d38c;
            }
            .badge-low {
                background: var(--low-bg);
                color: var(--low-text);
                border-color: #f2b7bd;
            }
            .compare-box {
                background: #fbfcfe;
                border: 1px solid var(--line);
                border-radius: 16px;
                padding: 0.95rem 1rem;
                min-height: 220px;
            }
            .compare-label {
                font-size: 0.8rem;
                text-transform: uppercase;
                letter-spacing: 0.09em;
                color: var(--muted);
                font-weight: 700;
                margin-bottom: 0.55rem;
            }
            .compare-copy {
                color: var(--text);
                white-space: pre-wrap;
                margin: 0;
            }
            .footer-card {
                margin-top: 1.2rem;
                text-align: center;
                color: var(--muted);
                font-size: 0.93rem;
            }
            div.stButton > button {
                border-radius: 14px;
                min-height: 2.8rem;
                border: none;
                font-weight: 700;
                background: linear-gradient(135deg, #0f766e, #173a5e);
                color: white;
            }
            div[data-baseweb="select"] > div,
            .stTextArea textarea {
                border-radius: 14px;
            }
            .stExpander {
                border: 1px solid var(--line);
                border-radius: 16px;
                background: rgba(255, 255, 255, 0.65);
            }
            div[data-testid="stMarkdownContainer"] ul {
                padding-left: 1.1rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def initialize_state() -> None:
    """Seed session state with the first sample."""
    first_sample = SAMPLE_EXAMPLES[0]
    st.session_state.setdefault("answer_text", first_sample["answer"])
    st.session_state.setdefault("source_text", first_sample["source_text"])
    st.session_state.setdefault("context_value", first_sample["context"])
    st.session_state.setdefault("selected_sample", first_sample["name"])
    st.session_state.setdefault("analysis_result", None)


def apply_selected_sample() -> None:
    """Copy the selected sample into the editable input fields."""
    sample_name = st.session_state.selected_sample
    for sample in SAMPLE_EXAMPLES:
        if sample["name"] == sample_name:
            st.session_state.answer_text = sample["answer"]
            st.session_state.source_text = sample["source_text"]
            st.session_state.context_value = sample["context"]
            break


def get_sample_description(sample_name: str) -> str:
    """Return the short description for the selected sample."""
    for sample in SAMPLE_EXAMPLES:
        if sample["name"] == sample_name:
            return sample.get("description", "")
    return ""


def render_bullets(items: list[str], empty_message: str) -> None:
    """Render a clean bullet list."""
    if not items:
        st.write(f"- {empty_message}")
        return
    for item in items:
        st.markdown(f"- {item}")


def badge_class(badge_label: str) -> str:
    """Map trust labels to CSS classes."""
    if "High" in badge_label:
        return "badge-high"
    if "Medium" in badge_label:
        return "badge-medium"
    return "badge-low"


def render_header() -> None:
    """Render the title and positioning copy."""
    st.markdown(
        """
        <div class="hero-card">
            <div class="eyebrow">Responsible AI Review</div>
            <div class="hero-title">TrustLens</div>
            <p class="hero-subtitle">
                A deterministic Streamlit tool that helps students judge whether an AI-generated answer is trustworthy
                enough to submit, cite, or revise.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_responsible_ai_banner() -> None:
    """Render the required compliance notice."""
    st.markdown(
        """
        <div class="banner">
            <div class="banner-title">Responsible AI Notice</div>
            <p class="banner-copy">
                TrustLens is an assistive evaluation tool. It does not replace human judgment, it does not guarantee
                factual correctness, and users should verify claims against reliable sources before submitting,
                citing, or relying on an answer.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_input_panel() -> bool:
    """Render the input workflow and return whether analysis was requested."""
    left_col, right_col = st.columns([1.3, 0.9], gap="large")

    with left_col:
        with st.container(border=True):
            st.markdown('<div class="section-label">Input Workspace</div>', unsafe_allow_html=True)
            st.markdown(
                '<div class="section-title">Paste an answer and optional source text</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                '<p class="mini-note">TrustLens keeps the workflow on one screen so you can demo the full review loop quickly.</p>',
                unsafe_allow_html=True,
            )

            sample_col, button_col = st.columns([1.4, 0.8], gap="small")
            with sample_col:
                st.selectbox(
                    "Quick sample",
                    [sample["name"] for sample in SAMPLE_EXAMPLES],
                    key="selected_sample",
                    on_change=apply_selected_sample,
                    help="Load a built-in example to demonstrate a strong, medium, or risky answer.",
                )
            with button_col:
                st.write("")
                st.button(
                    "Load Sample",
                    use_container_width=True,
                    on_click=apply_selected_sample,
                )

            st.markdown(
                f'<span class="sample-note">{get_sample_description(st.session_state.selected_sample)}</span>',
                unsafe_allow_html=True,
            )

            st.text_area(
                "AI-generated answer",
                key="answer_text",
                height=210,
                placeholder="Paste the AI-generated answer you want to evaluate...",
            )
            st.text_area(
                "Optional source text",
                key="source_text",
                height=190,
                placeholder="Paste the article, notes, rubric, or source passage you want to compare against...",
            )
            st.selectbox(
                "Use case",
                ["Class Assignment", "Research", "Career / Job Prep", "General Use"],
                key="context_value",
            )

            analyze_clicked = st.button("Analyze Answer Trust", type="primary", use_container_width=True)
            st.caption("Deterministic rule-based scoring. The same input produces the same result.")

    with right_col:
        st.markdown(
            """
            <div class="panel-card">
                <div class="section-label">Demo Focus</div>
                <div class="section-title">What judges can see in under three minutes</div>
                <p class="mini-note">
                    TrustLens scores risk signals, shows evidence gaps, surfaces safer wording, and documents its own
                    limits. The interface is designed to make compliance and explainability visible without turning the
                    product into a black box.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="panel-card" style="margin-top: 1rem;">
                <div class="section-label">Checks Covered</div>
                <p class="mini-note">
                    Unsupported certainty, vague attribution, missing source support, overgeneralization, answer-source
                    mismatch, and unsupported numbers, dates, or named claims.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    return analyze_clicked


def render_results(result: AnalysisResult) -> None:
    """Render the analysis output in a polished, structured layout."""
    st.markdown("---")
    score_col, summary_col = st.columns([0.9, 1.1], gap="large")

    with score_col:
        with st.container(border=True):
            st.markdown(
                f"""
                <div class="score-panel">
                    <div class="score-kicker">Trust Score</div>
                    <div class="score-value">{result.score}/100</div>
                    <span class="trust-badge {badge_class(result.badge)}">{result.badge}</span>
                    <p class="score-copy">
                    This score reflects rule-based risk signals and evidence alignment, not factual verification.<br>
                    Higher scores indicate stronger alignment and fewer detected risks.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with summary_col:
        with st.container(border=True):
            st.markdown('<div class="section-label">Top Risk Signals</div>', unsafe_allow_html=True)
            render_bullets(result.flagged_issues[:3], "No major concerns detected.")
            st.markdown("")
            st.markdown("**Recommendation Summary**")
            st.write(result.recommendation_summary)

    evidence_col, rewrite_col = st.columns([0.95, 1.05], gap="large")

    with evidence_col:
        with st.container(border=True):
            st.markdown(
                '<div class="section-label">Expected Evidence</div>',
                unsafe_allow_html=True,
            )
            st.markdown("**What an evaluator would expect to see**")
            render_bullets(result.missing_evidence, "No urgent evidence gaps were found.")

    with rewrite_col:
        with st.container(border=True):
            st.markdown('<div class="section-label">Safer Rewrite</div>', unsafe_allow_html=True)
            st.write(result.safer_rewrite)

    st.markdown("")
    st.markdown('<div class="section-label">Original Answer vs Safer Rewrite</div>', unsafe_allow_html=True)
    original_col, safer_col = st.columns(2, gap="large")

    with original_col:
        with st.container(border=True):
            st.markdown('<div class="compare-label">Original Answer</div>', unsafe_allow_html=True)
            st.write(st.session_state.answer_text)

    with safer_col:
        with st.container(border=True):
            st.markdown('<div class="compare-label">Safer Rewrite</div>', unsafe_allow_html=True)
            st.write(result.safer_rewrite)

    with st.expander("Explainability | How this score was calculated", expanded=False):
        st.write(
            "TrustLens uses plain-language heuristics rather than a black-box model. It checks for six main risk dimensions:"
        )
        st.markdown("- Unsupported certainty: wording that sounds more confident than the evidence shown.")
        st.markdown("- Vague attribution: references like 'experts say' without naming who the source is.")
        st.markdown("- Missing source support: no source passage or citation to verify the answer against.")
        st.markdown("- Overgeneralization: broad all-or-nothing statements that need scope or exceptions.")
        st.markdown("- Mismatch between answer and source text: the answer drifts away from the provided source.")
        st.markdown("- Unsupported numbers, dates, and named claims: specific details that are not backed by the source.")
        st.markdown("")
        st.markdown("**What affected this result**")
        render_bullets(result.explainers, "No additional score explanations were needed.")

    with st.expander("Validation Boundaries | Limitations of this analysis", expanded=False):
        st.markdown("- This tool is heuristic and rule-based.")
        st.markdown("- It does not check external databases or the live web.")
        st.markdown("- It cannot guarantee academic acceptance.")
        st.markdown("- It helps identify risk signals, not final truth.")

    with st.expander("Audit Trace", expanded=False):
        trace_col_a, trace_col_b = st.columns(2, gap="large")
        with trace_col_a:
            st.markdown("**Signals detected**")
            render_bullets(result.detected_signals, "No special signals were detected.")
            st.markdown("**Rules triggered**")
            render_bullets(result.triggered_rules, "No penalty rules were triggered.")
        with trace_col_b:
            st.markdown("**Negative score drivers**")
            render_bullets(result.negative_factors, "No negative score drivers were recorded.")
            st.markdown("**Positive score drivers**")
            render_bullets(result.positive_factors, "No positive context was recorded.")
        st.markdown("**Score breakdown**")
        render_bullets(result.score_breakdown, "No score breakdown was recorded.")


def render_footer() -> None:
    """Render the required footer branding."""
    st.markdown(
        """
        <div class="footer-card">
            TANO Research | Trust • Accuracy • Neutrality • Organization • Transparency
        </div>
        """,
        unsafe_allow_html=True,
    )


apply_styles()
initialize_state()
render_header()
render_responsible_ai_banner()

analyze_clicked = render_input_panel()

if analyze_clicked:
    st.session_state.analysis_result = analyze_trust(
        answer=st.session_state.answer_text,
        source_text=st.session_state.source_text,
        context=st.session_state.context_value,
    )

if st.session_state.analysis_result is not None:
    render_results(st.session_state.analysis_result)

render_footer()
