import pandas as pd

INPUT_FILE = "./data/raw/county_population.csv"
OUTPUT_FILE = "./data/cleaned/county_population_cleaned.csv"

KEEP_STATES = {
    "Colorado", "Connecticut", "Maine", "Minnesota", "Montana",
    "New Jersey", "New Mexico", "New York", "North Carolina",
    "Oregon", "Tennessee", "Texas", "Vermont", "Virginia"
}

STATE_MAP = {
    "Colorado": "CO",
    "Connecticut": "CT",
    "Maine": "ME",
    "Minnesota": "MN",
    "Montana": "MT",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "Oregon": "OR",
    "Tennessee": "TN",
    "Texas": "TX",
    "Vermont": "VT",
    "Virginia": "VA",
}

# load
df = pd.read_csv(INPUT_FILE, dtype=str)

# clean headers
df.columns = df.columns.str.strip()

# ensure County is text
df["County"] = df["County"].astype(str).str.strip()

# split "Adams County, Colorado"
split_cols = df["County"].str.rsplit(",", n=1, expand=True)
df["County_Name"] = split_cols[0].str.strip()
df["State"] = split_cols[1].str.strip()

# keep only your states
df = df[df["State"].isin(KEEP_STATES)].copy()

# clean county names
df["County"] = (
    df["County_Name"]
    .str.replace(" County", "", regex=False)
    .str.strip()
    .str.upper()
)

# fix Connecticut planning regions -> old county names
ct_map = {
    "CAPITOL PLANNING REGION": "HARTFORD",
    "GREATER BRIDGEPORT PLANNING REGION": "FAIRFIELD",
    "LOWER CONNECTICUT RIVER VALLEY PLANNING REGION": "MIDDLESEX",
    "NAUGATUCK VALLEY PLANNING REGION": "NEW HAVEN",
    "NORTHEASTERN CONNECTICUT PLANNING REGION": "WINDHAM",
    "NORTHWEST HILLS PLANNING REGION": "LITCHFIELD",
    "SOUTH CENTRAL CONNECTICUT PLANNING REGION": "NEW HAVEN",
    "SOUTHEASTERN CONNECTICUT PLANNING REGION": "NEW LONDON",
    "WESTERN CONNECTICUT PLANNING REGION": "FAIRFIELD",
}

df.loc[df["State"] == "Connecticut", "County"] = (
    df.loc[df["State"] == "Connecticut", "County"]
    .replace(ct_map)
)

# fix other known naming mismatches
df["County"] = (
    df["County"]
    .str.replace("DOÑA ANA", "DONA ANA", regex=False)
    .str.replace("DEWITT", "DE WITT", regex=False)
)

# convert state names to abbreviations
df["State"] = df["State"].map(STATE_MAP)

# population columns
pop_cols = [
    "2020_Population",
    "2021_Population",
    "2022_Population",
    "2023_Population",
    "2024_Population"
]

# clean numeric columns
for col in pop_cols:
    df[col] = pd.to_numeric(df[col].str.replace(",", "", regex=False), errors="coerce")

# drop junk rows if all population values are missing
df = df.dropna(subset=pop_cols, how="all")

# final columns
df = df[["State", "County"] + pop_cols]

# save
df.to_csv(OUTPUT_FILE, index=False)

print(f"Saved filtered file to: {OUTPUT_FILE}")
print(f"Rows remaining: {len(df)}")
print(df.head())
