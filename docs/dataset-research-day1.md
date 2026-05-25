# Day 1 — Dataset Research & Collection

**Feature:** Student Performance Prediction  
**Goal:** Download datasets, store under `/datasets`, read columns, understand features.

---

## Folder layout

```
datasets/
├── raw/                    # Original data (unchanged)
│   ├── student_performance/   # UCI: student-mat.csv, student-por.csv
│   └── oulad/                 # Manual: OULAD CSV exports
├── processed/              # Column reports, cleaned tables (Week 2+)
├── final/                  # ML-ready train/test exports (Week 2+)
└── scripts/
    ├── download_datasets.py
    └── inspect_datasets.py
```

---

## Dataset A — Student Performance (UCI)

| Field | Details |
|-------|---------|
| **Source** | [UCI Student Performance](https://archive.ics.uci.edu/dataset/320/student+performance) |
| **Files** | `student-mat.csv`, `student-por.csv` (semicolon-separated) |
| **Rows** | ~395 Math + ~649 Portuguese |
| **Target** | `G3` final grade (0–20) → scale to 0–100% for MentorMind |

### Column → product mapping

| MentorMind feature | UCI column | Notes |
|--------------------|------------|-------|
| Study hours | `studytime` | Ordinal 1–4, multiply ~1.5 for hours proxy |
| Attendance | `absences` | More absences = lower attendance % |
| Sleep | — | **Not available** — document gap; use `health` (1–5) as weak proxy |
| Assignments | `failures`, `activities` | Past failures + school activities |
| Marks | `G1`, `G2`, `G3` | Sequential grades; `G3` = prediction target |

### Other useful columns

`Medu`, `Fedu`, `traveltime`, `famrel`, `freetime`, `goout`, `Dalc`, `Walc`, `higher`, `internet`, `romantic`

---

## Dataset B — OULAD (Open University)

| Field | Details |
|-------|---------|
| **Source** | [OULAD](https://analyse.kmi.open.ac.uk/open_dataset) |
| **Use later** | Engagement, dropout risk, study-plan recommendations |
| **Setup** | Manual download (license) → extract to `datasets/raw/oulad/` |

### Key tables

| File | Purpose |
|------|---------|
| `studentInfo.csv` | Demographics, `final_result`, previous attempts |
| `studentAssessment.csv` | Scores per assessment |
| `assessments.csv` | Assessment metadata, weights, dates |
| `studentVle.csv` | VLE clicks — **study/engagement** signal |
| `courses.csv` | Module presentations |
| `studentRegistration.csv` | Registration dates |

---

## Commands (Day 1 TODO)

```bash
# 1. Download UCI + OULAD instructions
python datasets/scripts/download_datasets.py

# 2. Read columns & generate reports
python datasets/scripts/inspect_datasets.py
```

**Outputs:**

- `datasets/processed/columns_inventory.json`
- `datasets/processed/dataset_columns_report.md`

---

## Checklist

- [x] Folder structure: `raw/`, `processed/`, `final/`
- [x] Download UCI Student Performance (`download_datasets.py`)
- [ ] Manual OULAD download (optional — place CSVs in `datasets/raw/oulad/`)
- [x] Run column inspection (`inspect_datasets.py`)
- [x] Review feature mapping in this doc

---

## Next steps (Day 2+)

1. Clean missing values and outliers → `processed/`
2. Feature engineering (study_efficiency, attendance_pct)
3. Train/test split → `final/`
4. First sklearn / XGBoost pipeline
