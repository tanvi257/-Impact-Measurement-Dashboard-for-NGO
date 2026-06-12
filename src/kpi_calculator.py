import numpy as np
import pandas as pd


def add_calculated_fields(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    result["attendance_rate"] = safe_divide(
        result["beneficiaries_attended"], result["beneficiaries_registered"]
    )
    result["session_completion_rate"] = safe_divide(
        result["sessions_completed"], result["sessions_planned"]
    )
    result["score_gain"] = result["endline_score"] - result["baseline_score"]
    result["estimated_improved_beneficiaries"] = (
        result["beneficiaries_attended"] * result["score_gain"].clip(lower=0) / 100
    )
    result["cost_per_beneficiary"] = safe_divide(
        result["total_cost"], result["beneficiaries_attended"]
    )
    result["cost_per_improved_beneficiary"] = safe_divide(
        result["total_cost"], result["estimated_improved_beneficiaries"]
    )
    result["women_share"] = safe_divide(result["women_count"], result["beneficiaries_attended"])
    result["youth_share"] = safe_divide(result["youth_count"], result["beneficiaries_attended"])
    result["inclusion_share"] = safe_divide(
        result["sc_count"]
        + result["st_count"]
        + result["minority_count"]
        + result["persons_with_disability_count"],
        result["beneficiaries_attended"],
    )
    result["followup_rate"] = safe_divide(
        result["followup_completed"], result["beneficiaries_attended"]
    )
    return result.replace([np.inf, -np.inf], np.nan)


def safe_divide(numerator, denominator):
    return np.where(denominator == 0, np.nan, numerator / denominator)


def dashboard_summary(df: pd.DataFrame) -> dict:
    total_beneficiaries = int(df["beneficiaries_attended"].sum())
    total_cost = float(df["total_cost"].sum())
    improved = float(df["estimated_improved_beneficiaries"].sum())
    weighted_gain = weighted_average(df, "score_gain", "beneficiaries_attended")

    return {
        "beneficiaries": total_beneficiaries,
        "total_cost": total_cost,
        "estimated_improved": improved,
        "avg_score_gain": weighted_gain,
        "cost_per_beneficiary": total_cost / total_beneficiaries if total_beneficiaries else 0,
        "cost_per_improved": total_cost / improved if improved else 0,
        "session_completion": weighted_average(
            df, "session_completion_rate", "sessions_planned"
        ),
        "data_quality_issue_rate": (
            (df["data_quality_flag"].str.lower() != "clean").mean() if len(df) else 0
        ),
    }


def weighted_average(df: pd.DataFrame, value_col: str, weight_col: str) -> float:
    valid = df[[value_col, weight_col]].dropna()
    valid = valid[valid[weight_col] > 0]
    if valid.empty:
        return 0.0
    return float(np.average(valid[value_col], weights=valid[weight_col]))


def grouped_kpis(df: pd.DataFrame, by: str) -> pd.DataFrame:
    grouped = (
        df.groupby(by, as_index=False)
        .agg(
            beneficiaries_attended=("beneficiaries_attended", "sum"),
            total_cost=("total_cost", "sum"),
            estimated_improved_beneficiaries=("estimated_improved_beneficiaries", "sum"),
            avg_score_gain=("score_gain", "mean"),
            sessions_completed=("sessions_completed", "sum"),
            issue_count=("issue_count", "sum"),
        )
        .sort_values("estimated_improved_beneficiaries", ascending=False)
    )
    grouped["cost_per_beneficiary"] = (
        grouped["total_cost"] / grouped["beneficiaries_attended"]
    )
    grouped["cost_per_improved_beneficiary"] = (
        grouped["total_cost"] / grouped["estimated_improved_beneficiaries"]
    )
    return grouped.replace([np.inf, -np.inf], np.nan)


def data_quality_table(df: pd.DataFrame) -> pd.DataFrame:
    checks = pd.DataFrame(
        {
            "Check": [
                "Rows marked clean",
                "Rows with missing values",
                "Rows where attended exceeds registered",
                "Rows with zero planned sessions",
                "Rows with unresolved field issues",
            ],
            "Count": [
                int((df["data_quality_flag"].str.lower() == "clean").sum()),
                int(df.isna().any(axis=1).sum()),
                int((df["beneficiaries_attended"] > df["beneficiaries_registered"]).sum()),
                int((df["sessions_planned"] == 0).sum()),
                int((df["issue_count"] > 0).sum()),
            ],
        }
    )
    checks["Recommended action"] = [
        "No action needed.",
        "Ask field worker to complete missing fields before review.",
        "Verify attendance register and correct the entry.",
        "Confirm whether the activity was cancelled or entered incorrectly.",
        "Resolve issue notes before using the row for final reporting.",
    ]
    return checks
