import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score

# load data
df = pd.read_csv("data/final/master_dataset_model.csv")

# MODEL 1: Stations -> EV Growth
print("\nMODEL 1: Do stations predict EV growth?")

X = df[["Stations_per_10k_Lag1", "EV_per_10k_Lag1", "Year"]]
y = df["EV_per_10k_Growth"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestRegressor(random_state=42)
model.fit(X_train, y_train)

preds = model.predict(X_test)

print("R²:", round(r2_score(y_test, preds), 3))

importance = pd.DataFrame({
    "Feature": X.columns,
    "Importance": model.feature_importances_
}).sort_values("Importance", ascending=False)

print(importance)

# MODEL 2: EV -> Station Growth
print("\nMODEL 2: Do EVs predict station growth?")

X = df[["EV_per_10k_Lag1", "Stations_per_10k_Lag1", "Year"]]
y = df["Stations_per_10k_Growth"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestRegressor(random_state=42)
model.fit(X_train, y_train)

preds = model.predict(X_test)

print("R²:", round(r2_score(y_test, preds), 3))

importance = pd.DataFrame({
    "Feature": X.columns,
    "Importance": model.feature_importances_
}).sort_values("Importance", ascending=False)

print(importance)
