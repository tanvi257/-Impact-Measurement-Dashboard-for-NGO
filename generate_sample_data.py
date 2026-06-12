from pathlib import Path

import numpy as np
import pandas as pd


OUTPUT_PATH = Path("data/sample_field_data.csv")


def build_sample_data(seed=42):
    rng = np.random.default_rng(seed)

    districts = {
        "Haridwar": ["Bahadrabad", "Laksar", "Roorkee Rural"],
        "Dehradun": ["Raipur", "Doiwala", "Sahaspur"],
        "Pauri Garhwal": ["Kotdwar", "Dugadda", "Yamkeshwar"],
        "Tehri Garhwal": ["Chamba", "Narendranagar", "Pratapnagar"],
    }
    programs = [
        "Digital Literacy",
        "Health Awareness",
        "Skill Training",
        "Women Entrepreneurship",
    ]
    activity_types = ["Workshop", "Camp", "Follow-up Visit", "Training Session"]
    workers = [
        "FW-001",
        "FW-002",
        "FW-003",
        "FW-004",
        "FW-005",
        "FW-006",
        "FW-007",
        "FW-008",
    ]

    rows = []
    dates = pd.date_range("2026-01-05", "2026-05-31", freq="4D")

    record_id = 1
    for date in dates:
        for _ in range(rng.integers(2, 5)):
            district = rng.choice(list(districts.keys()))
            block = rng.choice(districts[district])
            program = rng.choice(programs, p=[0.28, 0.27, 0.25, 0.20])

            registered = int(rng.integers(35, 150))
            attendance_rate = rng.uniform(0.68, 0.95)
            attended = int(registered * attendance_rate)
            sessions_planned = int(rng.integers(1, 5))
            sessions_completed = int(max(0, sessions_planned - rng.choice([0, 0, 0, 1])))

            baseline = rng.normal(45, 10)
            program_lift = {
                "Digital Literacy": 18,
                "Health Awareness": 14,
                "Skill Training": 16,
                "Women Entrepreneurship": 20,
            }[program]
            endline = baseline + rng.normal(program_lift, 6)
            baseline = float(np.clip(baseline, 5, 95))
            endline = float(np.clip(endline, 5, 100))

            women_share = rng.uniform(0.45, 0.78)
            youth_share = rng.uniform(0.25, 0.62)
            sc_share = rng.uniform(0.10, 0.28)
            st_share = rng.uniform(0.02, 0.12)
            minority_share = rng.uniform(0.04, 0.22)
            pwd_share = rng.uniform(0.01, 0.05)

            cost_per_person = rng.normal(210, 45)
            fixed_cost = rng.normal(1800, 400)
            total_cost = max(2500, attended * cost_per_person + fixed_cost)

            issue_count = int(rng.choice([0, 0, 0, 1, 1, 2], p=[0.55, 0.18, 0.10, 0.09, 0.05, 0.03]))
            if issue_count == 0:
                flag = "Clean"
            else:
                flag = rng.choice(["Missing follow-up", "Attendance mismatch", "Late entry"])

            rows.append(
                {
                    "record_id": f"REC-{record_id:04d}",
                    "date": date.date().isoformat(),
                    "district": district,
                    "block": block,
                    "program": program,
                    "activity_type": rng.choice(activity_types),
                    "field_worker": rng.choice(workers),
                    "beneficiaries_registered": registered,
                    "beneficiaries_attended": attended,
                    "sessions_planned": sessions_planned,
                    "sessions_completed": sessions_completed,
                    "baseline_score": round(baseline, 1),
                    "endline_score": round(endline, 1),
                    "women_count": int(attended * women_share),
                    "youth_count": int(attended * youth_share),
                    "sc_count": int(attended * sc_share),
                    "st_count": int(attended * st_share),
                    "minority_count": int(attended * minority_share),
                    "persons_with_disability_count": int(attended * pwd_share),
                    "total_cost": round(total_cost, 0),
                    "followup_completed": int(attended * rng.uniform(0.55, 0.90)),
                    "issue_count": issue_count,
                    "data_quality_flag": flag,
                }
            )
            record_id += 1

    return pd.DataFrame(rows)


def main():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df = build_sample_data()
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Wrote {len(df)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
