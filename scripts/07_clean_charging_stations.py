import pandas as pd
from pathlib import Path

RAW_DIR = Path("data/raw")
OUT_DIR = Path("data/cleaned")
OUT_DIR.mkdir(parents=True, exist_ok=True)

stations_file = RAW_DIR / "charging_stations.csv"
zip_file = RAW_DIR / "ZIP_COUNTY.csv"
lookup_file = RAW_DIR / "county_code_lookup_selected_states_old_ct_counties.csv"
output_file = OUT_DIR / "charging_stations_county.csv"

TARGET_STATES = {"VA","VT","TX","TN","ME","MN","MT","NJ","NM","NY","NC","OR","CT","CO"}

def clean_zip(series):
    return (
        series.astype(str)
        .str.strip()
        .str.replace(".0", "", regex=False)
        .str.extract(r"(\d+)", expand=False)
        .str.zfill(5)
    )

def clean_code(series):
    return (
        series.astype(str)
        .str.strip()
        .str.replace(".0", "", regex=False)
        .str.extract(r"(\d+)", expand=False)
        .str.zfill(5)
    )

# ----------------------------
# LOAD
# ----------------------------
stations = pd.read_csv(stations_file, dtype=str)
zip_df = pd.read_csv(zip_file, dtype=str)
lookup = pd.read_csv(lookup_file, dtype=str)

stations.columns = stations.columns.str.strip()
zip_df.columns = zip_df.columns.str.strip()
lookup.columns = lookup.columns.str.strip()

# ----------------------------
# FIX COLUMN NAMES (IMPORTANT)
# ----------------------------
if "State" not in stations.columns:
    if "State/Province" in stations.columns:
        stations = stations.rename(columns={"State/Province": "State"})
    elif "State Code" in stations.columns:
        stations = stations.rename(columns={"State Code": "State"})

if "ZIP" not in stations.columns:
    if "ZIP Code" in stations.columns:
        stations = stations.rename(columns={"ZIP Code": "ZIP"})

# ----------------------------
# CLEAN CORE COLUMNS
# ----------------------------
stations["State"] = stations["State"].str.strip().str.upper()
stations["ZIP"] = clean_zip(stations["ZIP"])

zip_df["State"] = zip_df["State"].str.strip().str.upper()
zip_df["ZIP Code"] = clean_zip(zip_df["ZIP Code"])
zip_df["County"] = clean_code(zip_df["County"])
zip_df["TOT_RATIO"] = pd.to_numeric(zip_df["TOT_RATIO"], errors="coerce")

lookup["State"] = lookup["State"].str.strip().str.upper()
lookup["County"] = clean_code(lookup["County"])
lookup["County Name"] = lookup["County Name"].str.strip().str.upper()

# ----------------------------
# FILTER DATA
# ----------------------------
stations = stations[stations["State"].isin(TARGET_STATES)].copy()

if "Fuel Type Code" in stations.columns:
    stations = stations[stations["Fuel Type Code"] == "ELEC"].copy()

stations = stations[
    stations["ZIP"].notna() &
    (stations["ZIP"] != "") &
    (stations["ZIP"] != "NAN")
]

# ----------------------------
# ZIP → COUNTY CODE
# ----------------------------
zip_best = (
    zip_df[zip_df["State"].isin(TARGET_STATES)]
    .sort_values(["State","ZIP Code","TOT_RATIO"], ascending=[True,True,False])
    .drop_duplicates(subset=["State","ZIP Code"])
)

zip_best = zip_best.rename(columns={"County":"County_Code"})

merged = stations.merge(
    zip_best[["State","ZIP Code","County_Code"]],
    left_on=["State","ZIP"],
    right_on=["State","ZIP Code"],
    how="left"
)

print("Missing County_Code:", merged["County_Code"].isna().sum())

# ----------------------------
# COUNTY CODE → COUNTY NAME
# ----------------------------
merged = merged.merge(
    lookup[["State","County","County Name"]],
    left_on=["State","County_Code"],
    right_on=["State","County"],
    how="left"
)

print("Missing County Name:", merged["County Name"].isna().sum())

# ----------------------------
# FINAL CLEAN
# ----------------------------
merged["County"] = merged["County Name"]

merged = merged.drop(
    columns=["ZIP Code","County_Code","County Name"],
    errors="ignore"
)

merged.to_csv(output_file, index=False)

print("Saved to:", output_file)
print(merged[["State","ZIP","County"]].head())
