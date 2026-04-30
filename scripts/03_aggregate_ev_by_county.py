import pandas as pd
from pathlib import Path

# ----------------------------
# DIRECTORIES
# ----------------------------
CLEAN_DIR = Path("data/cleaned")
OUT_DIR = Path("data/final")
OUT_DIR.mkdir(parents=True, exist_ok=True)

files = sorted(CLEAN_DIR.glob("*_EV_county.csv"))

# ----------------------------
# PROCESS EACH CLEANED STATE FILE
# ----------------------------
for file in files:
    print(f"\nProcessing {file.name}")

    df = pd.read_csv(file, dtype=str)
    df.columns = df.columns.str.strip()

    required_cols = {"State", "County", "Vehicle Count", "Registration Date"}
    missing_cols = required_cols - set(df.columns)
    if missing_cols:
        print(f"Skipped {file.name}: missing columns {missing_cols}")
        continue

    df["State"] = df["State"].astype(str).str.strip().str.upper()
    df["County"] = df["County"].astype(str).str.strip().str.upper()
    df["Vehicle Count"] = pd.to_numeric(df["Vehicle Count"], errors="coerce").fillna(0)

    # convert registration date to year
    df["Registration Date"] = pd.to_datetime(df["Registration Date"], errors="coerce")
    df["Year"] = df["Registration Date"].dt.year

    # remove bad county rows
    df = df[
        df["County"].notna() &
        (df["County"] != "") &
        (df["County"] != "NAN")
    ]

    # remove bad year rows
    df = df[df["Year"].notna()].copy()
    df["Year"] = df["Year"].astype(int)

    # keep only 2020-2024
    df = df[(df["Year"] >= 2020) & (df["Year"] <= 2024)].copy()

    county_totals = (
        df.groupby(["State", "County", "Year"], as_index=False)["Vehicle Count"]
        .sum()
        .rename(columns={"Vehicle Count": "EV_Count"})
    )

    print("Number of county-year rows:", len(county_totals))
    print(county_totals.head())

    if county_totals.empty:
        print(f"Skipped {file.name}: no valid rows after filtering.")
        continue

    state_abbr = county_totals["State"].iloc[0]
    out_file = OUT_DIR / f"{state_abbr}_EV_county_aggregated.csv"
    county_totals.to_csv(out_file, index=False)

    print("Saved state file to:", out_file)
