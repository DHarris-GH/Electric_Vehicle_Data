#!/bin/bash
#SBATCH --job-name=EV_Pipeline
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --time=30
#SBATCH --mem=16G
#SBATCH -o ./logs/EV_Pipeline_%j.out
#SBATCH -e ./logs/EV_Pipeline_%j.err

# Stop if any step fails
set -e

# Create logs folder if it doesn't exist
mkdir -p logs

echo "Starting EV data pipeline..."
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $(hostname)"
echo "Start time: $(date)"


# LOAD ENVIRONMENT
module load miniforge3
conda activate ev_env

echo "Using Python:"
which python3
python3 --version


echo "Starting EV data pipeline..."

echo "1. Downloading datasets..."
python3 scripts/01_download_datasets.py

echo "2. Cleaning EV data..."
python3 scripts/02_data_cleaning.py

echo "3. Aggregating EV data by county and year..."
python3 scripts/03_aggregate_ev_by_county.py

echo "4. Merging EV state files..."
python3 scripts/04_merge_ev_states.py

echo "5. Cleaning county population data..."
python3 scripts/05_county_population_cleaning.py

echo "6. Reshaping population data by year..."
python3 scripts/06_reshape_population_by_year.py

echo "7. Cleaning charging station data..."
python3 scripts/07_clean_charging_stations.py

echo "8. Counting charging stations by county..."
python3 scripts/08_count_charging_stations_by_county.py

echo "9. Aggregating charging stations by county and year..."
python3 scripts/09_aggregate_charging_by_county_year.py

echo "10. Merging EV, population, and charging data..."
python3 scripts/10_merge_all_data.py

echo "11. Filling missing county-year combinations..."
python3 scripts/11_fill_missing_county_years.py

echo "12. Creating growth and lag features..."
python3 scripts/12_create_growth_features.py

echo "13. Running Random Forest models..."
python3 scripts/13_run_random_forest.py

echo "14. Creating visualizations..."
python3 scripts/14_visualize_animation.py

echo "Pipeline complete."
