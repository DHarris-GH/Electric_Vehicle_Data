from pathlib import Path
import gdown

DATA_DIR = Path("data/raw")
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Crosswalk + lookup
ZIP_COUNTY_ID = "1cO0HeLiLsIAeuwk5I_HU2LwLiUpNwCM-"
LOOKUP_ID = "1TH2_eid82bAahoMooAf4cH-X1KsXgjf5"
COUNTY_POP_ID = "1T1ttxSd-76WNFPltcArABhiIho48IBrj"
CHARGING_STATION_ID = "1BOASM5Vpzigsom9un0EMrKf8l77gWkxo"

# State EV registration files
STATE_FILES = {
    "CO": "1-z6T0376oSlO9omaXwC4ZMOB1pDBfCRd",
    "CT": "1PI72_nZRENKSsHl-HFC7aVuqvAa4vEoK",
    "ME": "1yuofoj5rawJhywpkrCkBj4c_3MsZaHKW",
    "MN": "1fGCz1hTG5bXI7eOVDyAgohpNLslV60hY",
    "MT": "1C6RQM4hcHXQTCVP7ykjEn3wIIc-EUHrB",
    "NJ": "13g1H6rGrMwTb4BITL9YeiQZzdjmH6omA",
    "NM": "18zs-jL-qM2XVu1vvXuTNLVPZtYM8jrLa",
    "VA": "1A8xO9801jQv0lrcNUhAJOj9hICi-S2aL",
    "VT": "12L3TRjqjEKETYVBY1-VIwECeZXkXG5YD",
    "NC": "1wVjDNTpMTxQ9aUkaPviV8ZsnHT9Gx7fx",
    "OR": "1mV4xWCeCwgyt5LqudH4vSScmr79dLxcu",
    "TN": "1Z85X2alO431T6Cf-3Pwu7NrJVSkPA6d2",
    "TX": "1Kw3wYhvmSE9bR8llUwujovvaoM3Ss6Ph",
    "NY": "17TbiauUshPFMWJYRHFOS8sFlI04HRsUw",
}

def download_drive(file_id: str, out_path: Path) -> None:
    url = f"https://drive.google.com/uc?id={file_id}"
    gdown.download(url, str(out_path), quiet=False)

def assert_not_html(path: Path) -> None:
    if path.suffix.lower() == ".csv":
        text = path.read_text(errors="ignore")[:500].lower()
        if "<html" in text or "<!doctype html" in text:
            raise ValueError(f"{path} downloaded as HTML, not the real file.")

print("Downloading ZIP crosswalk...")
download_drive(ZIP_COUNTY_ID, DATA_DIR / "ZIP_COUNTY.csv")
assert_not_html(DATA_DIR / "ZIP_COUNTY.csv")

print("Downloading county lookup...")
download_drive(LOOKUP_ID, DATA_DIR / "county_code_lookup_selected_states_old_ct_counties.csv")
assert_not_html(DATA_DIR / "county_code_lookup_selected_states_old_ct_counties.csv")

print("Downloading county population...")
download_drive(COUNTY_POP_ID, DATA_DIR / "county_population.csv")
assert_not_html(DATA_DIR / "county_population.csv")

print("Downloading charging stations...")
download_drive(CHARGING_STATION_ID, DATA_DIR / "charging_stations.csv")
assert_not_html(DATA_DIR / "charging_stations.csv")

for state, file_id in STATE_FILES.items():
    out_file = DATA_DIR / f"{state}_EV.csv"
    print(f"Downloading {state}...")
    download_drive(file_id, out_file)
    assert_not_html(out_file)

print("\nDone.")
for p in sorted(DATA_DIR.iterdir()):
    print(p.name)

