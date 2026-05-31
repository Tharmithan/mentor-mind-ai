#!/usr/bin/env bash
# Send weekly report emails (Week 8 · Bonus)
# Requires SMTP env vars — see backend/.env.example
set -euo pipefail

BASE="${API_URL:-http://127.0.0.1:8000}"
USER_ID="${1:-demo-user-001}"
EMAIL="${2:-}"

if [[ -z "$EMAIL" ]]; then
  echo "Usage: $0 [user_id] recipient@email.com"
  echo "Env: SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, REPORT_EMAIL_FROM"
  exit 1
fi

echo "Sending weekly report for $USER_ID to $EMAIL …"
curl -s -X POST "$BASE/api/reports/weekly/$USER_ID/email?to_email=$EMAIL" | python3 -m json.tool
