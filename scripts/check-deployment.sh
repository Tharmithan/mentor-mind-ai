#!/usr/bin/env bash
# Smoke-test a deployed MentorMind stack (Week 8 · Day 1)
# Usage: ./scripts/check-deployment.sh https://your-api.railway.app [https://your-app.vercel.app]

set -euo pipefail

API_URL="${1:-http://localhost:8000}"
FRONTEND_URL="${2:-}"

API_URL="${API_URL%/}"

echo "=== MentorMind Deployment Check ==="
echo "API: $API_URL"
echo ""

check() {
  local name="$1"
  local url="$2"
  local code
  code=$(curl -s -o /tmp/mm-check.json -w "%{http_code}" "$url" || echo "000")
  if [ "$code" = "200" ]; then
    echo "✅ $name ($code)"
    head -c 120 /tmp/mm-check.json; echo "..."
  else
    echo "❌ $name (HTTP $code)"
    cat /tmp/mm-check.json 2>/dev/null || true
    echo ""
  fi
}

check "Health" "$API_URL/api/health"
check "AI status" "$API_URL/api/ai/status"
check "OpenAPI root" "$API_URL/"

echo ""
echo "--- POST /api/predict ---"
PRED_CODE=$(curl -s -o /tmp/mm-predict.json -w "%{http_code}" \
  -X POST "$API_URL/api/predict" \
  -H "Content-Type: application/json" \
  -d '{"study_hours":5,"attendance":82,"sleep_hours":7}' || echo "000")
if [ "$PRED_CODE" = "200" ]; then
  echo "✅ Predict ($PRED_CODE)"
  python3 -c "import json; d=json.load(open('/tmp/mm-predict.json')); print('  prediction:', d.get('prediction'), '| model:', d.get('model_version'))" 2>/dev/null || cat /tmp/mm-predict.json
else
  echo "❌ Predict (HTTP $PRED_CODE)"
fi

if [ -n "$FRONTEND_URL" ]; then
  FRONTEND_URL="${FRONTEND_URL%/}"
  echo ""
  echo "--- Frontend: $FRONTEND_URL ---"
  FE_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL" || echo "000")
  if [ "$FE_CODE" = "200" ]; then
    echo "✅ Frontend home ($FE_CODE)"
  else
    echo "❌ Frontend home (HTTP $FE_CODE)"
  fi
  PROXY_CODE=$(curl -s -o /tmp/mm-proxy.json -w "%{http_code}" "$FRONTEND_URL/api/health" || echo "000")
  if [ "$PROXY_CODE" = "200" ]; then
    echo "✅ Frontend /api proxy ($PROXY_CODE)"
  else
    echo "⚠️  Frontend /api proxy (HTTP $PROXY_CODE) — set API_PROXY_URL on Vercel"
  fi
fi

echo ""
echo "Done."
