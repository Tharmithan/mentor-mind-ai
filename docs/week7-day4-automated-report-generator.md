# Week 7 · Day 4 — Automated Report Generator

**Goal:** Generate professional weekly and monthly reports with PDF export and optional email delivery.

---

## Weekly report

| Section | Source |
|---------|--------|
| Learning progress | Learning analytics + long-term memory |
| Interview performance | Interview session history |
| Skill growth | Subject mastery + progress deltas |
| Recommendations | Coach + personalized recommender |

## Monthly report

| Section | Source |
|---------|--------|
| Career readiness | Skill gaps + career match |
| Learning statistics | Analytics engine + profile |
| Improvement areas | Memory weaknesses + AI insights |

---

## Backend layout

```
backend/app/reports/
├── generator.py      # Aggregate data into report sections
├── templates.py      # Markdown templates
├── pdf_exporter.py   # fpdf2 PDF generation
├── email_sender.py   # SMTP email delivery
└── service.py        # Orchestration + file persistence
```

Reports saved to `uploads/reports/`.

---

## API

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/reports/weekly/{user_id}` | Weekly JSON + markdown |
| GET | `/api/reports/monthly/{user_id}` | Monthly JSON + markdown |
| POST | `/api/reports/weekly/{user_id}/pdf` | Download PDF |
| POST | `/api/reports/monthly/{user_id}/pdf` | Download PDF |
| POST | `/api/reports/weekly/{user_id}/email` | Email report |
| POST | `/api/reports/monthly/{user_id}/email` | Email report |

---

## PDF & email setup

```bash
pip install -r requirements-reports.txt
```

Email (optional `.env`):

```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@gmail.com
SMTP_PASSWORD=app-password
REPORT_EMAIL_TO=student@example.com
```

---

## Frontend

**`/coach`** → **Automated Reports** panel — generate, preview, download PDF, email.

---

## Smoke test

```bash
cd backend
pip install fpdf2
python -c "
import asyncio
from app.reports.generator import ReportGenerator

async def main():
    w = await ReportGenerator.weekly('demo-user-001')
    print(w.period_label)
    print(w.markdown[:200])

asyncio.run(main())
"
```

```bash
curl -X POST http://localhost:8000/api/reports/weekly/demo-user-001/pdf -o weekly.pdf
```
