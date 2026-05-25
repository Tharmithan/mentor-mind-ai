#!/usr/bin/env python3
"""
Day 1 — Download datasets into datasets/raw/

Usage (repo root):
  python datasets/scripts/download_datasets.py
  python datasets/scripts/download_datasets.py --uci-only
"""

from __future__ import annotations

import argparse
import io
import sys
import zipfile
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parents[2]
ROOT = REPO_ROOT / "datasets"
RAW = ROOT / "raw"
UCI_DIR = RAW / "student_performance"
OULAD_DIR = RAW / "oulad"

UCI_STUDENT_ZIP = (
    "https://archive.ics.uci.edu/ml/machine-learning-databases/00320/student.zip"
)

OULAD_SETUP = """
OULAD (Open University Learning Analytics Dataset)
==================================================
Too large for automatic download (~100MB+). Manual steps:

1. Visit: https://analyse.kmi.open.ac.uk/open_dataset
2. Accept license and download the dataset ZIP
3. Extract CSV files into:
   datasets/raw/oulad/

Expected files include:
  - studentInfo.csv
  - studentAssessment.csv
  - assessments.csv
  - courses.csv
  - studentRegistration.csv
  - studentVle.csv
  - vle.csv
"""


def download_uci_student_performance(force: bool = False) -> bool:
    UCI_DIR.mkdir(parents=True, exist_ok=True)
    mat = UCI_DIR / "student-mat.csv"
    por = UCI_DIR / "student-por.csv"

    if mat.exists() and por.exists() and not force:
        print(f"[OK] UCI Student Performance already in {UCI_DIR}")
        return True

    print(f"Downloading UCI Student Performance...")
    print(f"  URL: {UCI_STUDENT_ZIP}")
    try:
        resp = requests.get(UCI_STUDENT_ZIP, timeout=120)
        resp.raise_for_status()
        with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
            zf.extractall(UCI_DIR)
        print(f"[OK] Extracted to {UCI_DIR}")
        for f in sorted(UCI_DIR.glob("*.csv")):
            print(f"     - {f.name}")
        return True
    except Exception as exc:
        print(f"[FAIL] UCI download: {exc}")
        return False


def setup_oulad_instructions() -> None:
    OULAD_DIR.mkdir(parents=True, exist_ok=True)
    readme = OULAD_DIR / "DOWNLOAD_INSTRUCTIONS.txt"
    readme.write_text(OULAD_SETUP.strip() + "\n")
    csv_count = len(list(OULAD_DIR.glob("*.csv")))
    if csv_count:
        print(f"[OK] OULAD: {csv_count} CSV file(s) in {OULAD_DIR}")
    else:
        print(f"[INFO] OULAD: place CSV files in {OULAD_DIR}")
        print("       See DOWNLOAD_INSTRUCTIONS.txt")


def main() -> int:
    parser = argparse.ArgumentParser(description="Download Day 1 datasets")
    parser.add_argument("--uci-only", action="store_true")
    parser.add_argument("--force", action="store_true", help="Re-download UCI")
    args = parser.parse_args()

    RAW.mkdir(parents=True, exist_ok=True)
    print("=== Day 1: Dataset collection ===\n")

    uci_ok = download_uci_student_performance(force=args.force)
    if not args.uci_only:
        setup_oulad_instructions()

    print("\nNext step:")
    print("  python datasets/scripts/inspect_datasets.py")
    return 0 if uci_ok else 1


if __name__ == "__main__":
    sys.exit(main())
