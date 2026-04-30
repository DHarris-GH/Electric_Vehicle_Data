import pandas as pd

INPUT = "data/final/master_dataset_full.csv"
OUTPUT = "data/final/master_dataset_model.csv"

df = pd.read_csv(INPUT)

# sort for correct time order
df = df.sort_values(["State", "County", "Year"])

group_cols = ["State", "County"]

# growth (change from last year)
df["EV_per_10k_Growth"] = df.groupby(group_cols)["EV_per_10k_People"].diff()
df["Stations_per_10k_Growth"] = df.groupby(group_cols)["Stations_per_10k_People"].diff()

# lag  (previous year values)
df["EV_per_10k_Lag1"] = df.groupby(group_cols)["EV_per_10k_People"].shift(1)
df["Stations_per_10k_Lag1"] = df.groupby(group_cols)["Stations_per_10k_People"].shift(1)

# drop rows where lag/growth not defined (first year)
df = df.dropna()

df.to_csv(OUTPUT, index=False)

print("Saved to:", OUTPUT)
print("Rows:", len(df))
print(df.head())
