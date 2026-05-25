#!/usr/bin/env python3
"""
Day 2 — Data cleaning with Pandas.

Tasks: nulls, duplicates, rename columns, encode categoricals, normalize.

Usage (repo root):
  python datasets/scripts/clean_data.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
ROOT = REPO_ROOT / "datasets"
RAW = ROOT / "raw" / "student_performance"
PROCESSED = ROOT / "processed"

CLEANED_CSV = PROCESSED / "student_performance_cleaned.csv"
NORMALIZED_CSV = PROCESSED / "student_performance_normalized.csv"
REPORT_JSON = PROCESSED / "cleaning_report.json"

# yes/no columns in UCI dataset
YES_NO_COLS = [
    "school_support",
    "family_support",
    "extra_paid_classes",
    "extracurricular",
    "nursery_attended",
    "wants_higher_ed",
    "internet_access",
    "romantic_relationship",
]

# Columns to min-max normalize (0–1)
NORMALIZE_COLS = [
    "age",
    "mother_education",
    "father_education",
    "travel_time",
    "study_hours",
    "past_failures",
    "family_relationship",
    "free_time",
    "going_out",
    "weekend_alcohol",
    "weekday_alcohol",
    "wellness_score",
    "absences",
    "grade_period_1",
    "grade_period_2",
    "final_grade",
    "attendance_pct",
    "performance_pct",
]

RENAME_MAP = {
    "school": "school_code",
    "sex": "gender",
    "age": "age",
    "address": "address_type",
    "famsize": "family_size",
    "Pstatus": "parents_together",
    "Medu": "mother_education",
    "Fedu": "father_education",
    "Mjob": "mother_job",
    "Fjob": "father_job",
    "reason": "school_choice_reason",
    "guardian": "guardian",
    "traveltime": "travel_time",
    "studytime": "study_hours",
    "failures": "past_failures",
    "schoolsup": "school_support",
    "famsup": "family_support",
    "paid": "extra_paid_classes",
    "activities": "extracurricular",
    "nursery": "nursery_attended",
    "higher": "wants_higher_ed",
    "internet": "internet_access",
    "romantic": "romantic_relationship",
    "famrel": "family_relationship",
    "freetime": "free_time",
    "goout": "going_out",
    "Dalc": "weekday_alcohol",
    "Walc": "weekend_alcohol",
    "health": "wellness_score",
    "absences": "absences",
    "G1": "grade_period_1",
    "G2": "grade_period_2",
    "G3": "final_grade",
}


def load_raw() -> pd.DataFrame:
    frames = []
    for name, course in [("student-mat.csv", "mathematics"), ("student-por.csv", "portuguese")]:
        path = RAW / name
        if not path.exists():
            raise FileNotFoundError(f"Missing {path}. Run download_datasets.py first.")
        df = pd.read_csv(path, sep=";")
        df["course"] = course
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def remove_missing(df: pd.DataFrame) -> pd.DataFrame:
    """Drop rows with nulls; fill rare gaps in numeric cols with median."""
    before = len(df)
    df = df.dropna(how="all")
    numeric = df.select_dtypes(include=[np.number]).columns
    for col in numeric:
        if df[col].isna().any():
            df[col] = df[col].fillna(df[col].median())
    df = df.dropna(subset=["G1", "G2", "G3"], how="any")
    after = len(df)
    return df, {"rows_before": before, "rows_after_drop": after, "nulls_dropped": before - after}


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)
    df = df.drop_duplicates()
    return df, {"duplicates_removed": before - len(df), "rows_after": len(df)}


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.rename(columns=RENAME_MAP)
    return out


def encode_binary_yes_no(series: pd.Series) -> pd.Series:
    """yes -> 1, no -> 0"""
    return series.astype(str).str.strip().str.lower().map({"yes": 1, "no": 0})


def encode_categoricals(df: pd.DataFrame) -> pd.DataFrame:
    """
    Encode categoricals for ML.
    Example: gender male/female -> 0/1 (female=0, male=1).
    """
    out = df.copy()

    # Gender: F=0, M=1
    out["gender"] = out["gender"].astype(str).str.strip().str.upper().map({"F": 0, "M": 1})

    # School: GP=0, MS=1
    out["school_code"] = out["school_code"].astype(str).str.strip().map({"GP": 0, "MS": 1})

    # Address: U=0, R=1
    out["address_type"] = out["address_type"].astype(str).str.strip().map({"U": 0, "R": 1})

    # Parents together: T=1, A=0
    out["parents_together"] = out["parents_together"].astype(str).str.strip().map({"T": 1, "A": 0})

    # Family size LE3=0, GT3=1
    out["family_size"] = out["family_size"].astype(str).str.strip().map({"LE3": 0, "GT3": 1})

    # yes/no fields
    for col in YES_NO_COLS:
        if col in out.columns:
            out[col] = encode_binary_yes_no(out[col])

    # Course: mathematics=0, portuguese=1
    out["course"] = out["course"].map({"mathematics": 0, "portuguese": 1})

    # Low-cardinality jobs/reasons — label encode
    for col in ("mother_job", "father_job", "school_choice_reason", "guardian"):
        if col in out.columns:
            out[col] = pd.Categorical(out[col]).codes

    return out


def clip_outliers(df: pd.DataFrame, columns: list[str], lower=0.01, upper=0.99) -> pd.DataFrame:
    out = df.copy()
    clipped = {}
    for col in columns:
        if col not in out.columns or not pd.api.types.is_numeric_dtype(out[col]):
            continue
        lo, hi = out[col].quantile([lower, upper])
        n = int(((out[col] < lo) | (out[col] > hi)).sum())
        out[col] = out[col].clip(lo, hi)
        if n:
            clipped[col] = n
    return out, clipped


def add_derived_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    # Scale studytime 1–4 to approximate weekly hours
    out["study_hours"] = out["study_hours"] * 1.5
    # Attendance proxy from absences
    out["attendance_pct"] = np.clip(100 - out["absences"] * 1.2, 50, 100).round(1)
    # Performance on 0–100 scale (target for MentorMind)
    out["performance_pct"] = (out["final_grade"] / 20 * 100).clip(0, 100).round(1)
    out["at_risk"] = (out["performance_pct"] < 60).astype(int)
    return out


def normalize_minmax(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Min-max normalize selected numeric columns to [0, 1]."""
    out = df.copy()
    for col in columns:
        if col not in out.columns:
            continue
        lo, hi = out[col].min(), out[col].max()
        if hi > lo:
            out[f"{col}_norm"] = (out[col] - lo) / (hi - lo)
        else:
            out[f"{col}_norm"] = 0.0
    return out


def clean_pipeline() -> dict:
    print("=== Day 2: Data cleaning ===\n")

    raw = load_raw()
    report = {"raw_rows": len(raw), "raw_columns": list(raw.columns)}

    df, null_stats = remove_missing(raw)
    report["null_handling"] = null_stats

    df, dup_stats = remove_duplicates(df)
    report["duplicates"] = dup_stats

    df = rename_columns(df)
    report["renamed_columns"] = list(df.columns)

    numeric_outlier_cols = [
        "age",
        "study_hours",
        "past_failures",
        "absences",
        "grade_period_1",
        "grade_period_2",
        "final_grade",
        "wellness_score",
    ]
    df, clipped = clip_outliers(df, numeric_outlier_cols)
    report["outliers_clipped"] = clipped

    df = encode_categoricals(df)
    df = add_derived_features(df)
    report["rows_cleaned"] = len(df)
    report["encoded_example"] = {
        "gender": "female=0, male=1",
        "yes_no": "no=0, yes=1",
    }

    PROCESSED.mkdir(parents=True, exist_ok=True)
    df.to_csv(CLEANED_CSV, index=False)
    print(f"[OK] Cleaned: {CLEANED_CSV} ({len(df)} rows)")

    normalized = normalize_minmax(df, NORMALIZE_COLS)
    normalized.to_csv(NORMALIZED_CSV, index=False)
    print(f"[OK] Normalized: {NORMALIZED_CSV}")

    report["normalize_columns"] = [f"{c}_norm" for c in NORMALIZE_COLS if c in df.columns]
    REPORT_JSON.write_text(json.dumps(report, indent=2))
    print(f"[OK] Report: {REPORT_JSON}")

    print(f"\nSummary: {report['raw_rows']} raw -> {report['rows_cleaned']} cleaned rows")
    return report


def main() -> int:
    try:
        clean_pipeline()
        return 0
    except FileNotFoundError as exc:
        print(f"Error: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
