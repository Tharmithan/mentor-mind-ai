# Day 2 — Data Cleaning

**Goal:** Convert raw data into usable AI training data.

---

## Concepts covered

| Concept | What we do |
|---------|------------|
| **Null values** | Drop empty rows; median-fill rare numeric gaps |
| **Duplicate rows** | `drop_duplicates()` |
| **Outliers** | Clip to 1st–99th percentile on grades, absences, study hours |
| **Feature encoding** | `gender` F/M → 0/1, `yes`/`no` → 1/0, label-encode jobs |
| **Rename columns** | UCI names → clear snake_case (`studytime` → `study_hours`) |
| **Normalize** | Min-max scale to `[0, 1]` → `*_norm` columns |

---

## Gender encoding example

```python
# Before
gender: "F" / "M"

# After
gender: 0 / 1   # female=0, male=1
```

---

## Commands

```bash
# Script (repeatable pipeline)
python datasets/scripts/clean_data.py

# Jupyter (experimentation)
jupyter notebook notebooks/02_data_cleaning.ipynb
```

**Google Colab:** Upload `datasets/raw/student_performance/*.csv` or clone the repo.

---

## Outputs

| File | Description |
|------|-------------|
| `processed/student_performance_cleaned.csv` | Renamed, encoded, derived features |
| `processed/student_performance_normalized.csv` | + min-max `*_norm` columns |
| `processed/cleaning_report.json` | Before/after stats |

---

## Derived features (MentorMind-aligned)

| Column | Formula |
|--------|---------|
| `study_hours` | `studytime × 1.5` |
| `attendance_pct` | `clip(100 - absences × 1.2, 50, 100)` |
| `performance_pct` | `final_grade / 20 × 100` |
| `at_risk` | `1` if `performance_pct < 60` |

---

## Checklist

- [x] Remove missing values
- [x] Remove duplicates
- [x] Rename columns properly
- [x] Convert categorical values (0/1 encoding)
- [x] Normalize data (min-max)
- [x] Jupyter notebook for experimentation

---

## Next (Day 3+)

- EDA visualizations in notebook
- Feature engineering → `datasets/final/`
- Train/test split + first ML model
