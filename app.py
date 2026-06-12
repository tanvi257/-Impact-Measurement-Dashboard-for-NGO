from pathlib import Path

import pandas as pd
import streamlit as st
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.config import APP_TITLE, DEFAULT_DATA_PATH, KPI_TREE
from src.data_loader import apply_filters, load_dashboard_data
from src.kpi_calculator import (
    add_calculated_fields,
    dashboard_summary,
    data_quality_table,
    grouped_kpis,
)
from src.visuals import (
    demographic_chart,
    district_gap_chart,
    program_efficiency_chart,
    progress_chart,
)


st.set_page_config(page_title=APP_TITLE, layout="wide")


def money(value):
    return f"Rs. {value:,.0f}"


def number(value):
    return f"{value:,.0f}"


def percent(value):
    return f"{value * 100:,.1f}%"


@st.cache_data(show_spinner=False)
def cached_load(source_key, uploaded_file_bytes=None):
    if uploaded_file_bytes is None:
        return add_calculated_fields(load_dashboard_data(source_key))

    from io import BytesIO

    return add_calculated_fields(load_dashboard_data(BytesIO(uploaded_file_bytes)))


st.title(APP_TITLE)
st.caption(
    "A demo-ready dashboard for Challenge 5.1: converting raw field data into decision-ready NGO impact KPIs."
)

with st.sidebar:
    st.header("Data")
    uploaded = st.file_uploader(
        "Upload NGO field data CSV",
        type=["csv"],
        help="Leave empty to use the included anonymized sample dataset.",
    )

    if uploaded is not None:
        df = cached_load(uploaded.name, uploaded.getvalue())
        st.success("Uploaded dataset loaded.")
    else:
        df = cached_load(DEFAULT_DATA_PATH)
        st.info("Using included anonymized sample dataset.")

    st.header("Filters")
    programs = st.multiselect(
        "Programs",
        sorted(df["program"].dropna().unique()),
        default=sorted(df["program"].dropna().unique()),
    )
    districts = st.multiselect(
        "Districts",
        sorted(df["district"].dropna().unique()),
        default=sorted(df["district"].dropna().unique()),
    )
    date_range = st.date_input(
        "Date range",
        value=(df["date"].min().date(), df["date"].max().date()),
        min_value=df["date"].min().date(),
        max_value=df["date"].max().date(),
    )

if len(date_range) != 2:
    st.warning("Please select both a start date and an end date.")
    st.stop()

filtered = apply_filters(df, programs, districts, date_range)

if filtered.empty:
    st.warning("No records match the selected filters.")
    st.stop()

summary = dashboard_summary(filtered)

st.subheader("Monday Executive Snapshot")
metric_1, metric_2, metric_3, metric_4 = st.columns(4)
metric_1.metric("Beneficiaries reached", number(summary["beneficiaries"]))
metric_2.metric("Estimated improved beneficiaries", number(summary["estimated_improved"]))
metric_3.metric("Cost per improved beneficiary", money(summary["cost_per_improved"]))
metric_4.metric("Average score gain", f"{summary['avg_score_gain']:.1f} points")

st.caption(
    "Recommended Monday number for the Executive Director: Cost per improved beneficiary. "
    "It combines reach, outcome quality, and cost efficiency in one decision metric."
)

tab_overview, tab_demographics, tab_quality, tab_impact, tab_data = st.tabs(
    [
        "Overview",
        "Demographic Reach",
        "Data Quality",
        "Impact Projection",
        "Data Dictionary",
    ]
)

with tab_overview:
    left, right = st.columns(2)
    with left:
        st.plotly_chart(progress_chart(filtered), use_container_width=True)
    with right:
        st.plotly_chart(
            program_efficiency_chart(grouped_kpis(filtered, "program")),
            use_container_width=True,
        )

    st.subheader("KPI Tree")
    st.dataframe(pd.DataFrame(KPI_TREE), use_container_width=True, hide_index=True)

    st.subheader("Program KPI Table")
    program_table = grouped_kpis(filtered, "program")
    st.dataframe(
        program_table[
            [
                "program",
                "beneficiaries_attended",
                "estimated_improved_beneficiaries",
                "avg_score_gain",
                "total_cost",
                "cost_per_beneficiary",
                "cost_per_improved_beneficiary",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )

with tab_demographics:
    left, right = st.columns(2)
    with left:
        st.plotly_chart(demographic_chart(filtered), use_container_width=True)
    with right:
        st.plotly_chart(
            district_gap_chart(grouped_kpis(filtered, "district")),
            use_container_width=True,
        )

    st.subheader("District KPI Table")
    district_table = grouped_kpis(filtered, "district")
    st.dataframe(district_table, use_container_width=True, hide_index=True)

with tab_quality:
    quality_summary = data_quality_table(filtered)
    issue_rate = summary["data_quality_issue_rate"]

    q1, q2, q3 = st.columns(3)
    q1.metric("Rows reviewed", number(len(filtered)))
    q2.metric("Data quality issue rate", percent(issue_rate))
    q3.metric("Field issues logged", number(filtered["issue_count"].sum()))

    st.subheader("Data Quality Checks")
    st.dataframe(quality_summary, use_container_width=True, hide_index=True)

    st.subheader("Rows Needing Review")
    review_rows = filtered[
        (filtered["data_quality_flag"].str.lower() != "clean")
        | (filtered["issue_count"] > 0)
        | (filtered["beneficiaries_attended"] > filtered["beneficiaries_registered"])
    ]
    if review_rows.empty:
        st.success("No high-priority data quality issues in the selected data.")
    else:
        st.dataframe(review_rows, use_container_width=True, hide_index=True)

with tab_impact:
    st.subheader("Impact Projection")
    current_months = max(1, filtered["month"].nunique())
    monthly_reach = summary["beneficiaries"] / current_months
    monthly_cost = summary["total_cost"] / current_months
    monthly_improved = summary["estimated_improved"] / current_months

    c1, c2, c3 = st.columns(3)
    scale_factor = c1.slider("Scale multiplier", 1.0, 5.0, 1.5, 0.1)
    months = c2.slider("Projection period in months", 3, 36, 12, 1)
    efficiency_gain = c3.slider("Expected efficiency gain", 0, 40, 10, 1)

    projected_reach = monthly_reach * scale_factor * months
    projected_cost = monthly_cost * scale_factor * months * (1 - efficiency_gain / 100)
    projected_improved = monthly_improved * scale_factor * months
    projected_cost_per_improved = (
        projected_cost / projected_improved if projected_improved else 0
    )

    p1, p2, p3, p4 = st.columns(4)
    p1.metric("Projected reach", number(projected_reach))
    p2.metric("Projected improved beneficiaries", number(projected_improved))
    p3.metric("Projected cost", money(projected_cost))
    p4.metric("Projected cost per impact", money(projected_cost_per_improved))

    st.info(
        "Projection formula: monthly baseline performance x scale multiplier x months, "
        "with the selected efficiency gain applied to cost."
    )

with tab_data:
    dictionary_path = Path("data_dictionary.csv")
    if dictionary_path.exists():
        st.subheader("Data Dictionary")
        st.dataframe(pd.read_csv(dictionary_path), use_container_width=True, hide_index=True)

    st.subheader("Filtered Field Data")
    st.dataframe(filtered, use_container_width=True, hide_index=True)

    st.download_button(
        "Download filtered data",
        data=filtered.to_csv(index=False),
        file_name="filtered_ngo_impact_data.csv",
        mime="text/csv",
    )
