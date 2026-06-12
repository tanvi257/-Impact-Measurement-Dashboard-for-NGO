import plotly.express as px

from src.config import PROGRAM_COLORS


def progress_chart(df):
    weekly = (
        df.groupby("week", as_index=False)
        .agg(
            beneficiaries_attended=("beneficiaries_attended", "sum"),
            estimated_improved_beneficiaries=("estimated_improved_beneficiaries", "sum"),
        )
        .sort_values("week")
    )
    return px.line(
        weekly,
        x="week",
        y=["beneficiaries_attended", "estimated_improved_beneficiaries"],
        markers=True,
        labels={
            "week": "Week",
            "value": "People",
            "variable": "Metric",
        },
        title="Weekly reach and estimated improvement",
    )


def program_efficiency_chart(program_kpis):
    return px.bar(
        program_kpis.sort_values("cost_per_improved_beneficiary"),
        x="program",
        y="cost_per_improved_beneficiary",
        color="program",
        color_discrete_map=PROGRAM_COLORS,
        labels={
            "program": "Program",
            "cost_per_improved_beneficiary": "Cost per improved beneficiary",
        },
        title="Impact efficiency by program",
    )


def demographic_chart(df):
    totals = (
        df.groupby("program", as_index=False)
        .agg(
            women_count=("women_count", "sum"),
            youth_count=("youth_count", "sum"),
            sc_count=("sc_count", "sum"),
            st_count=("st_count", "sum"),
            minority_count=("minority_count", "sum"),
            persons_with_disability_count=("persons_with_disability_count", "sum"),
            beneficiaries_attended=("beneficiaries_attended", "sum"),
        )
        .sort_values("program")
    )
    for column in [
        "women_count",
        "youth_count",
        "sc_count",
        "st_count",
        "minority_count",
        "persons_with_disability_count",
    ]:
        totals[column] = totals[column] / totals["beneficiaries_attended"] * 100

    melted = totals.melt(
        id_vars=["program"],
        value_vars=[
            "women_count",
            "youth_count",
            "sc_count",
            "st_count",
            "minority_count",
            "persons_with_disability_count",
        ],
        var_name="Group",
        value_name="Share",
    )
    melted["Group"] = melted["Group"].str.replace("_count", "", regex=False).str.replace(
        "_", " "
    )
    return px.bar(
        melted,
        x="program",
        y="Share",
        color="Group",
        barmode="group",
        labels={"program": "Program", "Share": "Share of attended beneficiaries (%)"},
        title="Demographic reach",
    )


def district_gap_chart(district_kpis):
    return px.scatter(
        district_kpis,
        x="beneficiaries_attended",
        y="avg_score_gain",
        size="total_cost",
        color="district",
        hover_data=[
            "cost_per_beneficiary",
            "cost_per_improved_beneficiary",
            "issue_count",
        ],
        labels={
            "beneficiaries_attended": "Beneficiaries attended",
            "avg_score_gain": "Average outcome score gain",
        },
        title="District performance: reach vs outcome gain",
    )
