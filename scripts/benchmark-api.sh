#!/usr/bin/env bash
# Measure API latency (Week 8 · Day 4)
set -euo pipefail

BASE="${1:-http://127.0.0.1:8000}"
RUNS="${2:-5}"

echo "Benchmarking $BASE ($RUNS runs per endpoint)"
echo "-------------------------------------------"

bench() {
  local method="$1"
  local path="$2"
  local body="${3:-}"
  local label="$method $path"
  local total=0
  local i

  for ((i = 1; i <= RUNS; i++)); do
    if [[ -n "$body" ]]; then
      ms=$(curl -s -o /dev/null -w "%{time_total}" -X "$method" \
        -H "Content-Type: application/json" \
        -d "$body" "$BASE$path")
    else
      ms=$(curl -s -o /dev/null -w "%{time_total}" -X "$method" "$BASE$path")
    fi
    total=$(echo "$total + $ms" | bc)
  done

  avg=$(echo "scale=1; ($total / $RUNS) * 1000" | bc)
  printf "%-32s avg %6.0f ms\n" "$label" "$avg"
}

bench GET  "/api/health"
bench GET  "/api/ai/status"
bench GET  "/api/insights"
bench POST "/api/predict" '{"study_hours":6,"attendance":90,"sleep_hours":8}'
bench GET  "/api/documents"
bench GET  "/api/interview/types"
bench GET  "/api/metrics/latency"

echo ""
echo "Server-side summary:"
curl -s "$BASE/api/metrics/latency" | python3 -m json.tool 2>/dev/null || true
