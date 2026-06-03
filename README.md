# Neuropulse: Workforce Decision Safety Dashboard

Neuropulse is an interactive Dash dashboard for exploring the Human Decision Fatigue Behavioral Dataset from an HR analytics perspective. It helps a course instructor or reviewer reproduce the visualization work, inspect the enriched dataset, and interact with the same dashboard used in the project presentation.

The dashboard focuses on workforce wellbeing, decision fatigue, risk profiles, workload/confounding analysis, and intervention/recovery patterns. It uses linked Plotly views, filters, target-variable selection, heatmaps, scatter plots, line charts, box plots, and parallel coordinates.

## Repository Status

This directory is already initialized as a Git repository. The current working branch is intended for the project work, and the code can be pushed later after review.

## Project Structure

```text
Data_Visualization/
|-- data/
|   |-- raw/
|   |   |-- human_decision_fatigue_dataset.csv
|   |   `-- human_decision_fatigue_dataset_enriched.csv
|   `-- processed/
|       `-- human_decision_fatigue_dataset_with_anomalies.csv
|-- src/
|   `-- dashboard/
|       |-- app.py              # Dash entry point
|       |-- components.py       # Plotly chart definitions
|       |-- data_loader.py      # Dataset loading and feature engineering
|       |-- layout.py           # Dashboard layout, tabs, filters
|       |-- selection.py        # Brushing/selection helpers
|       `-- theme.py            # Styling helpers
|-- visualization_EngD_module_project_final_report/
|   |-- main.tex
|   `-- images/
|-- requirements.txt
`-- README.md
```

## Dataset

The project uses the Kaggle Human Decision Fatigue Behavioral Dataset and an enriched version stored in:

```text
data/raw/human_decision_fatigue_dataset_enriched.csv
```

The dashboard loads this enriched CSV by default. Additional derived variables are generated at runtime in `src/dashboard/data_loader.py`, including:

- `Decision_Density`
- `Hydration_Ratio`
- `Sleep_Deficit`
- `Fatigue_Risk_Index`
- grouped variables such as `Sleep_Group`, `Gym_Group`, `Caffeine_Group`, `Hydration_Group`, `Sugar_Group`, and `Break_Group`
- anomaly cohorts used to make the visual analysis less predictable and more useful for storytelling

## Requirements

Use Python 3.10 or newer. The dashboard was developed with the packages listed in `requirements.txt`:

```text
dash
dash-bootstrap-components
numpy
pandas
plotly
scikit-learn
```

## Setup

First open a terminal and move to the repository root. This is the folder created when the project repository is cloned or extracted. It contains `README.md`, `requirements.txt`, `data/`, and `src/`.

Use `cd` to enter that folder:

```powershell
cd path\to\Data_Visualization
```

You can confirm you are in the correct location by running:

```powershell
dir
```

You should see files/folders such as:

```text
README.md
requirements.txt
data
src
```

Then create and activate the virtual environment.

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

On macOS/Linux, first move to the repository root:

```bash
cd /path/to/Data_Visualization
```

Then run:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run the Dashboard

Make sure the terminal is still in the repository root:

```powershell
cd path\to\Data_Visualization
```

Then run:

```powershell
python src/dashboard/app.py
```

Then open:

```text
http://127.0.0.1:8050/
```

If port `8050` is already in use, stop the existing process or change the port at the bottom of `src/dashboard/app.py`.

## What to Inspect

The dashboard has four final tabs:

1. **Wellbeing**  
   Overview of fatigue, stress, sleep, mood, and system recommendations.

2. **Risk Profile**  
   Risk-focused views using cognitive load, decision density, sleep, gym activity, and target outcomes.

3. **Workload & Confounding**  
   Parallel coordinates and linked scatter/box views for investigating multivariate confounding patterns.

4. **Intervention and recovery**  
   Intervention-focused views for caffeine, hydration, snacks, breaks, sleep, gym activity, and selected output variables.

Use the left filter panel to choose:

- a dynamic filter category and values
- how plots are colored
- the target outcome variable, such as error rate, decision time, cognitive load, stress, or mood

Graph interactions are tab-local. Selecting, zooming, clicking, or using legends in one tab updates the other graphs in that same tab without changing unrelated tabs. The **Clear selection** button resets interactive selections back to the current left-filtered context.

## Reproducing the Project Results

To reproduce the dashboard results:

1. Clone or open this repository.
2. Install dependencies from `requirements.txt`.
3. Run `python src/dashboard/app.py`.
4. Open `http://127.0.0.1:8050/`.
5. Use the tab views and left-side filters to reproduce the analysis described in the report and presentation.

Recommended interaction path for the Intervention and Recovery tab:

1. Select `Avg_Decision_Time_sec` or `Error_Rate` as the target variable.
2. Inspect physical recovery by comparing `Gym_Group` across `Sleep_Group`.
3. Inspect caffeine/hydration heatmaps to identify high-risk combinations.
4. Use graph selection or legend interaction to see how the other plots in the tab respond.
5. Click **Clear selection** to reset the tab.

## Troubleshooting

If the app cannot find the dataset, make sure you are running the command from the repository root:

```powershell
python src/dashboard/app.py
```

If imports fail, confirm that the virtual environment is active and dependencies were installed:

```powershell
pip install -r requirements.txt
```

If the browser does not update after code changes, stop the Dash process and restart it.
