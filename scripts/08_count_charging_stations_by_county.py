import pandas as pd
from pathlib import Path

clean_file = Path("data/cleaned/charging_stations_county.csv")
out_file = Path("data/final/charging_stations_by_county.csv")
out_file.parent.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(clean_file, dtype=str)
df.columns = df.columns.str.strip()

# clean key columns
df["State"] = df["State"].astype(str).str.strip().str.upper()
df["County"] = df["County"].astype(str).str.strip().str.upper()

# remove rows without county
df = df[
    df["County"].notna() &
    (df["County"] != "") &
    (df["County"] != "NAN")
].copy()

# numeric charging columns
if "EV Level2 EVSE Num" in df.columns:
    df["EV Level2 EVSE Num"] = pd.to_numeric(df["EV Level2 EVSE Num"], errors="coerce").fillna(0)
else:
    df["EV Level2 EVSE Num"] = 0

if "EV DC Fast Count" in df.columns:
    df["EV DC Fast Count"] = pd.to_numeric(df["EV DC Fast Count"], errors="coerce").fillna(0)
else:
    df["EV DC Fast Count"] = 0

# total ports
df["Total_EV_Ports"] = df["EV Level2 EVSE Num"] + df["EV DC Fast Count"]

# count by county
county_counts = (
    df.groupby(["State", "County"], as_index=False)
    .agg(
        Charging_Station_Sites=("ZIP", "count"),
        Charging_Ports=("Total_EV_Ports", "sum"),
        DC_Fast_Ports=("EV DC Fast Count", "sum"),
        Level2_Ports=("EV Level2 EVSE Num", "sum")
    )
)

county_counts.to_csv(out_file, index=False)

print("Saved to:", out_file)
print("Rows:", len(county_counts))
print(county_counts.head())
