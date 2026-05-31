# Week 6 · Day 4 — Resume Analyzer

**Goal:** A recruiter-impressive feature — upload a PDF resume and get instant AI analysis of skills, ATS compatibility, formatting, and weak descriptions.

---

## Flow

```
Upload PDF (or paste text)
        ↓
Resume Parser — extract text + sections
        ↓
ATS Scorer — compatibility checks
        ↓
Skill Gap + Weak Bullet heuristics
        ↓
AI Feedback Generator (LLM + fallback)
        ↓
Full report with grade + actionable tips
```

---

## What AI checks

| Check | Description |
|-------|-------------|
| **Missing skills** | Gaps vs target role (AI Engineer, Data Scientist, etc.) |
| **ATS compatibility** | Contact info, sections, keywords, metrics, length |
| **Formatting** | Section headers, page length, ALL-CAPS, technical keywords |
| **Weak descriptions** | Passive verbs, bullets without quantified impact |

---

## Example output

```
Grade B (72/100 ATS)

Add more AI project metrics and technical achievements.

Missing skills:
• Machine Learning (high) — Highlight ML coursework or Kaggle projects
• Docker (medium) — Note containerized deployments

Weak descriptions:
• Missing quantified impact — Add users served, % improvement, time saved
```

---

## Backend

```
backend/app/resume/
├── parser.py       # PDF/text extraction, section parsing, bullet extraction
├── ats_scorer.py   # 7 ATS heuristic checks → score + grade
├── analyzer.py     # Full orchestration + persistence
└── feedback.py     # LLM feedback with heuristic fallback

backend/app/routes/resume.py
backend/app/models/resume.py
backend/app/agents/resume_agent.py  # Chat integration
```

Analyses saved to `backend/uploads/resumes/{analysis_id}.json`.

---

## API

| Method | Route | Description |
|--------|-------|-------------|
| `POST` | `/api/resume/upload` | Upload PDF/TXT → full analysis |
| `POST` | `/api/resume/analyze` | Analyze pasted text |
| `GET` | `/api/resume/analysis/{id}` | Retrieve saved analysis |

Query param: `target_role` = `ai_engineer` | `data_scientist` | `mlops` | `software_engineer`

---

## Frontend

| Path | Component |
|------|-----------|
| `/resume` | `ResumeAnalyzer` — drag-drop upload, ATS ring, feedback cards |
| Sidebar | "Resume Analyzer" nav link |

API: `uploadResume()`, `analyzeResumeText()`, `getResumeAnalysis()`

---

## Try it

```bash
# Analyze pasted text
curl -s -X POST http://127.0.0.1:8000/api/resume/analyze \
  -H "Content-Type: application/json" \
  -d '{"text":"John Doe\njohn@email.com\n\nExperience\n- Helped with Python projects\n- Worked on team assignments\n\nSkills\nPython, Java","target_role":"ai_engineer"}' | jq '{grade:.ats_grade, score:.ats_score, headline:.headline}'

# Via Resume Agent chat
curl -s -X POST http://127.0.0.1:8000/api/agents/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Analyze my resume","resume_text":"..."}' 
```

Open **http://localhost:3000/resume** and upload your PDF.

---

## Next

- Side-by-side bullet rewrite suggestions
- Job description keyword matching
- Export improved resume as PDF
