APP_TITLE = "NGO Impact Measurement Dashboard"
DEFAULT_DATA_PATH = "data/sample_field_data.csv"

PROGRAM_COLORS = {
    "Digital Literacy": "#2563eb",
    "Health Awareness": "#16a34a",
    "Skill Training": "#f97316",
    "Women Entrepreneurship": "#c026d3",
}

KPI_TREE = [
    {
        "Level": "Activity",
        "KPI": "Sessions completed",
        "Question answered": "Did field activity happen as planned?",
        "Formula": "sessions_completed / sessions_planned",
    },
    {
        "Level": "Output",
        "KPI": "Beneficiaries attended",
        "Question answered": "How many people actually received the service?",
        "Formula": "sum(beneficiaries_attended)",
    },
    {
        "Level": "Outcome",
        "KPI": "Average score gain",
        "Question answered": "Did knowledge, behaviour, or capability improve?",
        "Formula": "average(endline_score - baseline_score)",
    },
    {
        "Level": "Impact",
        "KPI": "Estimated improved beneficiaries",
        "Question answered": "How many meaningful improvements did the programme create?",
        "Formula": "beneficiaries_attended * max(score_gain, 0) / 100",
    },
    {
        "Level": "Efficiency",
        "KPI": "Cost per improved beneficiary",
        "Question answered": "How efficiently was impact created?",
        "Formula": "total_cost / estimated_improved_beneficiaries",
    },
]
