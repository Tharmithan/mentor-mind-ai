# Datasets — Student Performance Prediction (Day 1)

Main AI feature: **predict student performance** from study behavior and academic signals.

## Folder structure

```
datasets/
├── raw/           # Original downloads (do not edit)
├── processed/     # Cleaned tables + column reports
├── final/         # ML-ready exports (Week 2+)
├── scripts/       # Download & inspect utilities
└── README.md
```

## Recommended datasets

| ID | Dataset | Source | Folder |
|----|---------|--------|--------|
| **A** | Student Performance | [UCI ML Repository](https://archive.ics.uci.edu/dataset/320/student+performance) | `raw/student_performance/` |
| **B** | Open University Learning Analytics (OULAD) | [Open University](https://analyse.kmi.open.ac.uk/open_dataset) | `raw/oulad/` |

## Quick start

```bash
# From repo root (Python 3.12+)
pip install pandas requests numpy   # or use backend venv

# Day 1
python datasets/scripts/download_datasets.py
python datasets/scripts/inspect_datasets.py

# Day 2
python datasets/scripts/clean_data.py

# Day 3
pip install -r datasets/requirements-eda.txt
python datasets/scripts/eda_analysis.py
jupyter notebook notebooks/03_eda_ai_insights.ipynb

# Day 4
python datasets/scripts/feature_engineering.py

# Day 5
python datasets/scripts/train_models.py
```

## Feature mapping (product goal)

| Our feature | Student Performance (UCI) | OULAD |
|-------------|----------------------------|-------|
| Study hours | `studytime` (1–4 scale) | `sum_click`, activity logs |
| Attendance | `absences` (inverse proxy) | `num_of_prev_attempts`, engagement |
| Sleep | *Not in UCI* — add survey later | *Not direct* |
| Assignments | `failures`, activities | `assessment` submissions |
| Marks | `G1`, `G2`, `G3` (0–20) | `final_score`, grades |

See [docs/dataset-research-day1.md](../docs/dataset-research-day1.md) for full column notes.

## Git policy

Large CSV/ZIP files under `raw/`, `processed/`, and `final/` are **gitignored**.  
Committed: structure, scripts, column reports (`processed/*.json`, `processed/*.md`).
