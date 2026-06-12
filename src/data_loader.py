from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = {
    "date",
    "district",
    "block",
    "program",
    "activity_type",
    "field_worker",
    "beneficiaries_registered",
    "beneficiaries_attended",
    "sessions_planned",
    "sessions_completed",
    "baseline_score",
    "endline_score",
    "women_count",
    "youth_count",
    "sc_count",
    "st_count",
    "minority_count",
    "persons_with_disability_count",
    "total_cost",
    "followup_completed",
    "issue_count",
    "data_quality_flag",
}


NUMERIC_COLUMNS = [
    "beneficiaries_registered",
    "beneficiaries_attended",
    "sessions_planned",
    "sessions_completed",
    "baseline_score",
    "endline_score",
    "women_count",
    "youth_count",
    "sc_count",
    "st_count",
    "minority_count",
    "persons_with_disability_count",
    "total_cost",
    "followup_completed",
    "issue_count",
]


def load_dashboard_data(source) -> pd.DataFrame:
    if hasattr(source, "read"):
        df = pd.read_csv(source)
    else:
        path = Path(source)
        if not path.exists():
            raise FileNotFoundError(f"Data file not found: {path}")
        df = pd.read_csv(path)

    missing = REQUIRED_COLUMNS.difference(df.columns)
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(sorted(missing)))

    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    for column in NUMERIC_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df = df.dropna(subset=["date", "district", "program"])
    df["month"] = df["date"].dt.to_period("M").astype(str)
    df["week"] = df["date"].dt.to_period("W").apply(lambda value: value.start_time)
    return df


def apply_filters(df: pd.DataFrame, programs, districts, date_range) -> pd.DataFrame:
    start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    filtered = df[
        df["program"].isin(programs)
        & df["district"].isin(districts)
        & (df["date"] >= start_date)
        & (df["date"] <= end_date)
    ]
    return filtered.copy()
