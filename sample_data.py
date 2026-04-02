"""Built-in demo examples for TrustLens."""

SAMPLE_EXAMPLES = [
    {
        "name": "Strong Summary With Source",
        "description": "A grounded summary that stays close to the source text.",
        "context": "Class Assignment",
        "answer": (
            "According to the provided article, sleep improves memory by helping the brain organize new information. "
            "The source explains that consistent sleep supports focus and learning in students."
        ),
        "source_text": (
            "The article states that sleep helps the brain consolidate new information into memory. "
            "Researchers also note that students who keep consistent sleep schedules often show better focus in class."
        ),
    },
    {
        "name": "Overconfident Career Advice",
        "description": "A risky answer with sweeping language and no supporting source.",
        "context": "Career / Job Prep",
        "answer": (
            "Experts say recruiters definitely reject every resume that is longer than one page, and this rule always "
            "applies in every industry."
        ),
        "source_text": "",
    },
    {
        "name": "Specific Claims That Drift From Source",
        "description": "An answer that sounds specific but overreaches beyond the provided source.",
        "context": "Research",
        "answer": (
            "The study proves that 78% of teenagers use AI every day in 2024, and schools in New York, Boston, and "
            "Chicago have already replaced traditional homework with AI tutors."
        ),
        "source_text": (
            "The report discusses growing student use of AI tools in schools. It mentions that some teachers are "
            "experimenting with AI tutors, but it does not provide national daily-use percentages or say that schools "
            "have replaced homework."
        ),
    },
]
