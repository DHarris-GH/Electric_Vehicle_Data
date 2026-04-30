import pandas as pd
from pathlib import Path

FINAL_DIR = Path("data/final")
OUT_FILE = FINAL_DIR / "ev_counts_by_county.csv"

files = sorted(FINAL_DIR.glob("*_EV_county_aggregated.csv"))

all_states = []

for file in files:
    print(f"Reading {file.name}")
    df = pd.read_csv(file, dtype=str)
    df.columns = df.columns.str.strip()

    required_cols = {"State", "County", "EV_Count"}
    missing_cols = required_cols - set(df.columns)
    if missing_cols:
        print(f"Skipped {file.name}: missing columns {missing_cols}")
        continue

    df["State"] = df["State"].astype(str).str.strip().str.upper()
    df["County"] = df["County"].astype(str).str.strip().str.upper()
    df["EV_Count"] = pd.to_numeric(df["EV_Count"], errors="coerce").fillna(0)

    all_states.append(df)

if not all_states:
    raise ValueError("No aggregated EV state files found.")

combined = pd.concat(all_states, ignore_index=True)

# safety check
dupes = combined.duplicated(subset=["State", "County"]).sum()
print("Duplicate State-County rows:", dupes)

combined.to_csv(OUT_FILE, index=False)

print("Saved to:", OUT_FILE)
print("Rows:", len(combined))
print(combined.head())
