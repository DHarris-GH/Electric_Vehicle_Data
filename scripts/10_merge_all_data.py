import pandas as pd
from pathlib import Path

EV_FILE = Path("data/final/ev_counts_by_county.csv")
CHARGING_FILE = Path("data/final/charging_stations_by_county_year.csv")
POP_FILE = Path("data/final/population_by_county_year.csv")

OUT_FILE = Path("data/final/master_dataset.csv")

# ----------------------------
# HELPER
# ----------------------------
def clean_county(name):
    name = str(name).upper().strip()

    # Preserve Virginia county named "CHARLES CITY"
    if name == "CHARLES CITY" or name == "CHARLES CITY COUNTY":
        return "CHARLES CITY"

    # Standardize common suffixes
    name = name.replace(" COUNTY", "")
    name = name.replace(" (CITY)", "")
    name = name.replace(" CITY", "")

    return name.strip()

# ----------------------------
# LOAD
# ----------------------------
ev = pd.read_csv(EV_FILE)
charging = pd.read_csv(CHARGING_FILE)
pop = pd.read_csv(POP_FILE)

# ----------------------------
# CLEAN EV
# ----------------------------
ev.columns = ev.columns.str.strip()
ev["State"] = ev["State"].astype(str).str.strip().str.upper()
ev["County"] = ev["County"].apply(clean_county)
ev["Year"] = pd.to_numeric(ev["Year"], errors="coerce").astype("Int64")
ev["EV_Count"] = pd.to_numeric(ev["EV_Count"], errors="coerce").fillna(0)

# ----------------------------
# CLEAN CHARGING
# ----------------------------
charging.columns = charging.columns.str.strip()
charging["State"] = charging["State"].astype(str).str.strip().str.upper()
charging["County"] = charging["County"].apply(clean_county)
charging["Year"] = pd.to_numeric(charging["Year"], errors="coerce").astype("Int64")

charging_cols = [
    "Charging_Station_Sites",
    "Charging_Ports",
    "DC_Fast_Ports",
    "Level2_Ports"
]

for col in charging_cols:
    charging[col] = pd.to_numeric(charging[col], errors="coerce").fillna(0)

# Combine duplicates that may appear after county-name cleaning
charging = (
    charging.groupby(["State", "County", "Year"], as_index=False)[charging_cols]
    .sum()
)

# ----------------------------
# CLEAN POPULATION
# ----------------------------
pop.columns = pop.columns.str.strip()
pop["State"] = pop["State"].astype(str).str.strip().str.upper()
pop["County"] = pop["County"].apply(clean_county)
pop["Year"] = pd.to_numeric(pop["Year"], errors="coerce").astype("Int64")
pop["Population"] = pd.to_numeric(pop["Population"], errors="coerce")

# Combine duplicates that may appear after county-name cleaning
pop = (
    pop.groupby(["State", "County", "Year"], as_index=False)["Population"]
    .sum()
)

# ----------------------------
# MERGE ALL THREE
# ----------------------------
merged = ev.merge(
    pop,
    on=["State", "County", "Year"],
    how="left"
)

merged = merged.merge(
    charging,
    on=["State", "County", "Year"],
    how="left"
)

for col in charging_cols:
    merged[col] = merged[col].fillna(0)

# ----------------------------
# CREATE METRICS
# ----------------------------
merged["EV_per_Station"] = merged["EV_Count"] / merged["Charging_Station_Sites"].replace(0, pd.NA)
merged["EV_per_Port"] = merged["EV_Count"] / merged["Charging_Ports"].replace(0, pd.NA)
merged["Stations_per_10k_People"] = (merged["Charging_Station_Sites"] / merged["Population"]) * 10000
merged["Ports_per_10k_People"] = (merged["Charging_Ports"] / merged["Population"]) * 10000
merged["EV_per_10k_People"] = (merged["EV_Count"] / merged["Population"]) * 10000

# ----------------------------
# SAVE
# ----------------------------
merged.to_csv(OUT_FILE, index=False)

print("Saved to:", OUT_FILE)
print("Rows:", len(merged))
print("Missing population:", merged["Population"].isna().sum())
print(merged.head())
