import pandas as pd
from pathlib import Path

INPUT_FILE = Path("data/cleaned/county_population_cleaned.csv")
OUTPUT_FILE = Path("data/final/population_by_county_year.csv")

df = pd.read_csv(INPUT_FILE, dtype=str)
df.columns = df.columns.str.strip()

df["State"] = df["State"].astype(str).str.strip().str.upper()
df["County"] = df["County"].astype(str).str.strip().str.upper()

pop_cols = [
    "2020_Population",
    "2021_Population",
    "2022_Population",
    "2023_Population",
    "2024_Population"
]

for col in pop_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

long_df = df.melt(
    id_vars=["State", "County"],
    value_vars=pop_cols,
    var_name="Year",
    value_name="Population"
)

long_df["Year"] = (
    long_df["Year"]
    .str.extract(r"(\d{4})", expand=False)
    .astype(int)
)

long_df["Population"] = pd.to_numeric(long_df["Population"], errors="coerce")
long_df = long_df.dropna(subset=["Population"])

long_df.to_csv(OUTPUT_FILE, index=False)

print("Saved to:", OUTPUT_FILE)
print("Rows:", len(long_df))
print(long_df.head())
