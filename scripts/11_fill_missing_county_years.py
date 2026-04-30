import pandas as pd

INPUT = "data/final/master_dataset.csv"
OUTPUT = "data/final/master_dataset_full.csv"

df = pd.read_csv(INPUT)

# ----------------------------
# CREATE FULL PANEL (ALL COUNTY-YEAR COMBINATIONS)
# ----------------------------

counties = df[["State", "County"]].drop_duplicates()
years = [2020, 2021, 2022, 2023, 2024]

full_index = (
    counties.assign(key=1)
    .merge(pd.DataFrame({"Year": years, "key": 1}), on="key")
    .drop("key", axis=1)
)

# ----------------------------
# MERGE WITH ORIGINAL DATA
# ----------------------------
df_full = full_index.merge(
    df,
    on=["State", "County", "Year"],
    how="left"
)

# ----------------------------
# FILL MISSING VALUES
# ----------------------------

fill_zero_cols = [
    "EV_Count",
    "Charging_Station_Sites",
    "Charging_Ports",
    "DC_Fast_Ports",
    "Level2_Ports"
]

for col in fill_zero_cols:
    df_full[col] = df_full[col].fillna(0)

# population should already exist, but just in case:
df_full["Population"] = df_full["Population"].ffill()

# ----------------------------
# RECOMPUTE METRICS (IMPORTANT)
# ----------------------------

df_full["EV_per_Station"] = df_full["EV_Count"] / df_full["Charging_Station_Sites"].replace(0, pd.NA)
df_full["EV_per_Port"] = df_full["EV_Count"] / df_full["Charging_Ports"].replace(0, pd.NA)

df_full["Stations_per_10k_People"] = (df_full["Charging_Station_Sites"] / df_full["Population"]) * 10000
df_full["Ports_per_10k_People"] = (df_full["Charging_Ports"] / df_full["Population"]) * 10000
df_full["EV_per_10k_People"] = (df_full["EV_Count"] / df_full["Population"]) * 10000

# ----------------------------
# SORT + SAVE
# ----------------------------

df_full = df_full.sort_values(["State", "County", "Year"])

df_full.to_csv(OUTPUT, index=False)

print("Saved to:", OUTPUT)
print("Rows:", len(df_full))

# sanity check
counts = df_full.groupby(["State", "County"])["Year"].nunique()
print("Min years per county:", counts.min())
print(df_full.head())
