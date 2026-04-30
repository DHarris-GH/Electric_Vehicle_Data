import pandas as pd
from pathlib import Path

INPUT_FILE = Path("data/cleaned/charging_stations_county.csv")
OUTPUT_FILE = Path("data/final/charging_stations_by_county_year.csv")

YEARS = [2020, 2021, 2022, 2023, 2024]

df = pd.read_csv(INPUT_FILE, dtype=str)
df.columns = df.columns.str.strip()

required_cols = {"State", "County", "ZIP", "Open Date"}
missing_cols = required_cols - set(df.columns)
if missing_cols:
    raise ValueError(f"Missing required columns: {missing_cols}")

df["State"] = df["State"].astype(str).str.strip().str.upper()
df["County"] = df["County"].astype(str).str.strip().str.upper()

df = df[
    df["County"].notna() &
    (df["County"] != "") &
    (df["County"] != "NAN")
].copy()

# parse open date
df["Open Date"] = pd.to_datetime(df["Open Date"], errors="coerce")
df["Open_Year"] = df["Open Date"].dt.year

# keep stations with valid open year
df = df[df["Open_Year"].notna()].copy()
df["Open_Year"] = df["Open_Year"].astype(int)

# numeric charging columns
if "EV Level2 EVSE Num" in df.columns:
    df["EV Level2 EVSE Num"] = pd.to_numeric(df["EV Level2 EVSE Num"], errors="coerce").fillna(0)
else:
    df["EV Level2 EVSE Num"] = 0

if "EV DC Fast Count" in df.columns:
    df["EV DC Fast Count"] = pd.to_numeric(df["EV DC Fast Count"], errors="coerce").fillna(0)
else:
    df["EV DC Fast Count"] = 0

df["Total_EV_Ports"] = df["EV Level2 EVSE Num"] + df["EV DC Fast Count"]

# use a station id if available; otherwise each row counts as one site
site_id_col = "ID" if "ID" in df.columns else "ZIP"

all_years = []

for year in YEARS:
    year_df = df[df["Open_Year"] <= year].copy()

    county_counts = (
        year_df.groupby(["State", "County"], as_index=False)
        .agg(
            Charging_Station_Sites=(site_id_col, "nunique" if site_id_col == "ID" else "count"),
            Charging_Ports=("Total_EV_Ports", "sum"),
            DC_Fast_Ports=("EV DC Fast Count", "sum"),
            Level2_Ports=("EV Level2 EVSE Num", "sum")
        )
    )

    county_counts["Year"] = year
    all_years.append(county_counts)

final_df = pd.concat(all_years, ignore_index=True)
final_df = final_df[
    [
        "State", "County", "Year",
        "Charging_Station_Sites",
        "Charging_Ports",
        "DC_Fast_Ports",
        "Level2_Ports"
    ]
]

final_df.to_csv(OUTPUT_FILE, index=False)

print("Saved to:", OUTPUT_FILE)
print("Rows:", len(final_df))
print(final_df.head())
