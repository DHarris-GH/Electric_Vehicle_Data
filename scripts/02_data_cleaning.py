import pandas as pd
from pathlib import Path

RAW_DIR = Path("data/raw")
OUT_DIR = Path("data/cleaned")
OUT_DIR.mkdir(parents=True, exist_ok=True)

ZIP_FILE = RAW_DIR / "ZIP_COUNTY.csv"
LOOKUP_FILE = RAW_DIR / "county_code_lookup_selected_states_old_ct_counties.csv"

STATE_FILES = {
    "CO": RAW_DIR / "CO_EV.csv",
    "CT": RAW_DIR / "CT_EV.csv",
    "ME": RAW_DIR / "ME_EV.csv",
    "MN": RAW_DIR / "MN_EV.csv",
    "MT": RAW_DIR / "MT_EV.csv",
    "NJ": RAW_DIR / "NJ_EV.csv",
    "NM": RAW_DIR / "NM_EV.csv",
    "VA": RAW_DIR / "VA_EV.csv",
    "VT": RAW_DIR / "VT_EV.csv",
    "NC": RAW_DIR / "NC_EV.csv",
    "OR": RAW_DIR / "OR_EV.csv",
    "TN": RAW_DIR / "TN_EV.csv",
    "TX": RAW_DIR / "TX_EV.csv",
    "NY": RAW_DIR / "NY_EV.csv",
}

# States that already have county names in their files
STATES_WITH_COUNTY_ALREADY = {"MT", "VA", "TN"}

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
# LOAD SHARED FILES
# ----------------------------
zip_df = pd.read_csv(ZIP_FILE, dtype=str)
lookup = pd.read_csv(LOOKUP_FILE, dtype=str)

zip_df.columns = zip_df.columns.str.strip()
lookup.columns = lookup.columns.str.strip()

zip_df["ZIP Code"] = clean_zip(zip_df["ZIP Code"])
zip_df["County"] = clean_code(zip_df["County"])
zip_df["State"] = zip_df["State"].astype(str).str.strip().str.upper()
zip_df["TOT_RATIO"] = pd.to_numeric(zip_df["TOT_RATIO"], errors="coerce")

lookup["State"] = lookup["State"].astype(str).str.strip().str.upper()
lookup["County"] = clean_code(lookup["County"])
lookup["County Name"] = lookup["County Name"].astype(str).str.strip().str.upper()

# ----------------------------
# PROCESS EACH STATE
# ----------------------------
for state_abbr, state_file in STATE_FILES.items():
    print(f"\n--- Processing {state_abbr} ---")

    df = pd.read_csv(state_file, dtype=str)
    df.columns = df.columns.str.strip()

    # Standardize State column
    if "State" not in df.columns:
        df["State"] = state_abbr
    df["State"] = df["State"].astype(str).str.strip().str.upper()

    # -------------------------------------------------
    # CASE 1: State file already has county names
    # -------------------------------------------------
    if state_abbr in STATES_WITH_COUNTY_ALREADY:
         if "County" not in df.columns:
             print(f"Skipped {state_abbr}: expected existing 'County' column but none found.")
             continue

         df["County"] = (
             df["County"]
            .astype(str)
            .str.strip()
            .str.upper()
            .str.replace(" COUNTY", "", regex=False)
         )

         out_file = OUT_DIR / f"{state_abbr}_EV_county.csv"
         df.to_csv(out_file, index=False)

         print("Used existing County column.")
         print("Saved to:", out_file)
         print("Original rows:", len(df))
         print("Output rows:", len(df))
         print("Missing counties:", df["County"].isna().sum())
         print(df.head())

         continue


    # -------------------------------------------------
    # CASE 2: State file needs ZIP -> county mapping
    # -------------------------------------------------
    if "ZIP Code" not in df.columns:
        print(f"Skipped {state_abbr}: no 'ZIP Code' column found.")
        continue

    df["ZIP Code"] = clean_zip(df["ZIP Code"])

    zip_state = zip_df[zip_df["State"] == state_abbr].copy()
    lookup_state = lookup[lookup["State"] == state_abbr].copy()

    zip_best = (
        zip_state.sort_values(["ZIP Code", "TOT_RATIO"], ascending=[True, False])
        .drop_duplicates(subset=["ZIP Code"])
        .copy()
    )

    zip_best = zip_best.rename(columns={"County": "County_Code"})

    merged = df.merge(
        zip_best[["ZIP Code", "County_Code"]],
        on="ZIP Code",
        how="left"
    )

    missing_code = merged["County_Code"].isna().sum()
    print("Missing County_Code after ZIP merge:", missing_code)

    merged = merged.merge(
        lookup_state[["County", "County Name"]],
        left_on="County_Code",
        right_on="County",
        how="left"
    )

    missing_name = merged["County Name"].isna().sum()
    print("Missing County Name after lookup merge:", missing_name)

    # Keep ZIP Code, add County
    merged["County"] = merged["County Name"]

    merged = merged.drop(
        columns=["County_Code", "County Name"],
        errors="ignore"
    )

    merged = merged.loc[:, ~merged.columns.duplicated()]

    out_file = OUT_DIR / f"{state_abbr}_EV_county.csv"
    merged.to_csv(out_file, index=False)

    print("Saved to:", out_file)
    print("Original rows:", len(df))
    print("Output rows:", len(merged))
    print("Missing counties:", merged["County"].isna().sum())
    print(merged.head())
