# TrustLens

<p class="hero-subtitle">
AI is powerful, but not always trustworthy. TrustLens helps students evaluate whether an AI-generated answer is safe to submit, cite, or rely on.
</p>

TrustLens is a deterministic Streamlit app that helps students judge whether an AI-generated answer is trustworthy enough to submit, cite, or revise.

<p class="hero-subtitle" style="margin-top:0.4rem; font-weight:600;">
TrustLens shifts AI usage from blind trust to informed decision-making.
</p>

## Why It Matters

AI-generated answers often sound confident and complete, even when they are unsupported or misleading. Students frequently rely on these responses without verifying them.

TrustLens introduces a lightweight, explainable review step that helps users detect risk signals, evaluate evidence alignment, and revise unsafe outputs before using them in academic or real-world contexts.

## Features

TrustLens focuses on fast, transparent evaluation rather than content generation.

- 📊 Prominent Trust Score with High, Medium, or Low Trust badge
- 🔎 Clear review sections for:
  - Top Concerns
  - What an evaluator would expect to see
  - Safer Rewrite
  - Audit Trace
- ⚠️ Deterministic rule-based checks for:
  - unsupported certainty
  - vague attribution
  - missing source support
  - overgeneralization
  - mismatch between answer and source text
  - unsupported numbers, dates, and named claims
- Plain-English Explainability section
- Validation Boundaries section
- Responsible AI banner and structured auditability

The app states this clearly in the score area:

> This score reflects rule-based risk signals and evidence alignment, not factual verification.

## Built With Codex

This project was built and refined using Codex for:

- scaffolding
- debugging
- scoring logic refinement
- UI iteration
- final polish and documentation

## Compliance-by-Design

TrustLens is designed to make responsible AI use visible in the product itself.

- Transparency: the app shows that scoring is deterministic and rule-based.
- Explainability: users can open "How this score was calculated" to see the logic in plain English.
- Safety: the interface states that TrustLens is assistive and does not replace human judgment.
- Validation boundaries: the app explains what it does not do, including live web verification.
- Auditability: the Audit Trace shows detected signals, triggered rules, and score drivers.
- Responsible use: users are directed to verify claims against reliable sources.

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Screenshots

### Home Screen
![Home Screen](assets/home.jpeg)

### Low Trust Example
![High Trust Result](assets/high.jpeg)

### High Trust Example
![Medium Trust Result](assets/medium.jpeg)

## Demo

🎥 Demo Video: (add your link here)  
🌐 Live App: ([TrustLens](https://trustlens-tano.streamlit.app/))

The demo shows how TrustLens evaluates a weak AI answer, highlights risk signals, and generates a safer rewrite in seconds.

## Future Improvements

- Sentence-level evidence highlighting
- Optional file upload for source text
- Exportable review summary for classroom use
- More sample scenarios for live demos

## Who It's For

- Students using AI for assignments or research
- Anyone who wants to validate AI-generated content before relying on it
- Users interested in responsible and transparent AI usage

TrustLens demonstrates how responsible AI principles can be embedded directly into user-facing tools.

---

**TANO Research**  
Trust • Accuracy • Neutrality • Organization • Transparency  
“Exploring Possibilities Everywhere”
