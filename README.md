# EV Adoption & Charging Infrastructure Analysis  
Selma Sulejmanovic and Dawn Harris 

---

##  Overview

This project builds a **data pipeline and modeling framework** to analyze the relationship between:

- Electric Vehicle (EV) adoption  
- Charging infrastructure availability  

The pipeline processes raw datasets, cleans and merges them, and applies **Random Forest models** to determine:

- Whether charging infrastructure influences EV adoption  
- Whether EV adoption influences infrastructure expansion  

---

##  Project Structure
ev_sd/
│
├── data/
│ ├── raw/ # Original downloaded datasets
│ ├── cleaned/ # Cleaned intermediate files
│ └── final/ # Final datasets for analysis
│
├── scripts/
│ ├── 01_download_datasets.py
│ ├── 02_data_cleaning.py
│ ├── 03_aggregate_ev_by_county.py
│ ├── 04_merge_ev_states.py
│ ├── 05_county_population_cleaning.py
│ ├── 06_reshape_population_by_year.py
│ ├── 07_clean_charging_stations.py
│ ├── 08_ count_charging_stations_by_county.py
│ ├── 09_aggregate_charging_by_county_year.py
│ ├── 10_merge_all_data.py
│ ├── 11_fill_missing_county_years.py
│ ├── 12_create_growth_features.py
│ ├── 13_run_random_forest.py
│ ├──
│ ├── 
│ └──
│
└── README.md


---

##  Data Sources

### 1. EV Registration Data
- State-level EV registration CSV files  
- Includes:
  - ZIP codes  
  - vehicle counts  
  - registration dates  

---

### 2. Charging Station Data
- Includes:
  - station locations  
  - number of ports  
  - open dates  

---

### 3. County Population Data
- U.S. Census dataset  
- Includes population from **2020–2024**

---

## Pipeline Description

---

### 1. Data Cleaning (`data_cleaning.py`)
- Cleans EV datasets  
- Maps ZIP codes → counties using lookup tables  
- Standardizes:
  - ZIP codes  
  - county codes  
  - state abbreviations  

---

### 2. Charging Data Processing (`clean_charging_stations.py`)
- Cleans charging station dataset  
- Extracts:
  - county  
  - state  
  - open date → converted to year  

---

### 3. Population Cleaning (`county_population_cleaning.py`)
- Extracts county + state  
- Converts population columns to numeric  
- Filters to selected states  

---

### 4. Reshape Population (`reshape_population_by_year.py`)
Converts population data:

**Wide → Long format**

Example:
2020, 2021, 2022 → Year column
Output:
State | County | Year | Population


---

### 5. EV Aggregation (`aggregate_ev_by_county.py`)
- Converts registration dates → year  
- Aggregates EV counts by:
  - State  
  - County  
  - Year  

---

### 6. Charging Aggregation (`count_charging_stations_by_county.py`)
- Groups charging stations by:
  - State  
  - County  
  - Year  
- Computes:
  - number of stations  
  - number of ports  

---

### 7. Merge All Data (`merge_all_data.py`)
Merges:
- EV data  
- Population data  
- Charging data  

Creates key metrics:
- EV_per_10k_People  
- Stations_per_10k_People  
- Ports_per_10k_People  
- EV_per_Station  
- EV_per_Port  

---

### 8. Fill Missing Years (`fill_missing_county_years.py`)
- Ensures every county has data for: 2020-2024

- Missing values handled as:
  - EV = 0  
  - Charging = 0  
  - Population = forward-filled  

---

### 9. Feature Engineering (`create_growth_features.py`)

Creates modeling variables:

**Growth variables:**
- EV_per_10k_Growth  
- Stations_per_10k_Growth  

**Lag variables:**
- EV_per_10k_Lag1  
- Stations_per_10k_Lag1  

These allow time-based modeling.

---

### 10. Modeling (`run_random_forest.py`)

Two Random Forest models are built:

---

#### Model 1:
EV Growth ~ Previous Charging Infrastructure


Tests:
> Does charging availability drive EV adoption?

---

#### Model 2:
Station Growth ~ Previous EV Adoption


Tests:
> Does EV demand drive infrastructure expansion?

---

## 🤖 Model Results

### Model 1 (Stations → EV Growth)
- **R² ≈ 0.56 (strong)**  

**Findings:**
- EV adoption is primarily driven by existing EV levels  
- Charging infrastructure plays a secondary role  

---

### Model 2 (EV → Station Growth)
- **R² ≈ 0.17 (weak)**  

**Findings:**
- EV demand alone does not strongly explain infrastructure growth  
- Expansion is likely influenced by policy, funding, and planning  

---

##  Key Insights


---

## How to Run

*Environment must have Python*

python3 -m pip install --user pandas gdown
pip3 install --user scikit-learn
pip install pandas seaborn matplotlib pillow


Run pipline.sh  to run all scripts in this order:

```bash
python3 scripts/01_download_datasets.py
python3 scripts/02_data_cleaning.py
python3 scripts/03_aggregate_ev_by_county.py
python3 scripts/04_merge_ev_states.py
python3 scripts/05_county_population_cleaning.py
python3 scripts/06_reshape_population_by_year.py
python3 scripts/07_clean_charging_stations.py
python3 scripts/08_count_charging_stations_by_county.py
python3 scripts/09_aggregate_charging_by_county_year.py
python3 scripts/10_merge_all_data.py 
python3 scripts/11_fill_missing_county_years.py 
python3 scripts/12_create_growth_features.py
python3 scripts/13_run_random_forest.py 
python3 scripts/
python3 scripts/ 



### Reflection

## Challenges
- Data was downloaded as HTML instead of CSV
- Converting to CSV removed leading zeros in ZIP codes
- CT now has planning regions instead of counties (inconsistent with older data)
- County_Population dataset was missing column names
- VA has independent cities as well as counties, causing inconsistencies

## What We Learned


