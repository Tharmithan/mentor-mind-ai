#!/usr/bin/env bash
# Run MentorMind backend test suite (Week 8 · Day 3)
set -euo pipefail
cd "$(dirname "$0")/../backend"
pip install -q -r requirements.txt -r requirements-test.txt
pytest -v --tb=short "$@"
