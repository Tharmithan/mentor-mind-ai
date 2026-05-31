# MentorMind AI — User Guide

> How to use the platform as a student.

---

## Getting Started

1. Open the app at **http://localhost:3000** (or your deployed Vercel URL).
2. Explore the main areas from the navigation bar or dashboard sidebar.
3. Optional: register at `/api/auth/register` (via API) or use demo mode without login.

**Demo credentials (when DB is unavailable):**
- Email: `student@mentormind.ai`
- Password: `Demo123!`

---

## Dashboard (`/dashboard`)

Your learning command center.

| Section | What it does |
|---------|--------------|
| **Performance score** | Overview of current academic standing |
| **Study analytics** | Charts for hours, subjects, trends |
| **ML Predict** | Enter study hours, attendance, sleep → get predicted score and risk |
| **Study planner** | AI-generated daily study plan |
| **AI insights** | Personalized tips based on your profile |

**Tip:** Lower sleep and attendance increase burnout and risk scores in predictions.

---

## AI Assistant (`/assistant`)

Upload your course notes and chat with an AI tutor grounded in *your* materials.

### Upload notes

1. Click **Upload** in the documents panel.
2. Supported: PDF, TXT, MD (max 25 MB).
3. Wait for processing — chunks are indexed for search.

### Ask questions

1. Select a document (or leave unselected for all notes).
2. Type a question in the chat panel, e.g. *"Explain recursion with an example from my notes."*
3. The assistant retrieves relevant chunks and generates an answer with sources.

### Study tools tab

- **Summarize** — condense a document
- **Quiz** — generate practice questions
- **Flashcards** — create review cards
- **Explain** — simplify a concept

---

## Interview Coach (`/interview`)

Practice mock interviews before real ones.

### Start a session

1. Choose type: **HR**, **Technical**, or **Behavioral**.
2. Set number of questions (1–10).
3. Read each question and type or record your answer.

### Tips for better scores

- Use the **STAR method** for behavioral questions (Situation, Task, Action, Result).
- Enable camera for optional emotion/confidence feedback.
- Use voice recording for speech-to-text transcription.

### After the interview

- View per-question scores and feedback.
- Open the **Coach report** for a summary improvement plan.

---

## AI Coach (`/coach`)

Unified hub for career and learning intelligence.

| Panel | Purpose |
|-------|---------|
| Score cards | Performance, communication, technical, confidence |
| Personalization | Learning style profile and recommendations |
| Memory | Long-term progress tracking |
| Learning analytics | Trends and subject comparisons |
| MLOps | Model versions and experiment history |
| Monitoring | Feedback and satisfaction metrics |
| Skill gaps | Topics to improve for your target career |
| Weekly report | Progress summary |

Set your target career (default: AI Engineer) for tailored recommendations.

---

## Learning Planner (`/planner`)

Generate a personalized roadmap:

1. Enter your goal (e.g. "Become a data scientist").
2. Set timeline and current skill level.
3. Review the generated weekly milestones and track progress.

---

## Resume Analyzer (`/resume`)

1. Upload your resume (PDF).
2. Optionally set a target role.
3. Review ATS score, keyword gaps, and improvement suggestions.

---

## Floating AI Assistant

Available on every page (bottom-right). Quick access to the multi-agent chat:

- **Study** — tutoring and planning
- **Interview** — practice tips
- **Career** — path and skill advice
- **Resume** — review guidance

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| "Could not load dashboard" | Start backend: `uvicorn app.main:app --port 8000` |
| Chat gives generic answers | Set `OPENAI_API_KEY` in backend `.env` for LLM mode |
| Upload fails | Check file type (PDF/TXT/MD) and size (< 25 MB) |
| Interview STT unavailable | Install interview deps: `pip install -r requirements-interview.txt` |
| Slow first request | Normal — models warm up on startup (Week 8 performance) |

---

## Privacy Notes

- Uploaded documents are stored locally on the server (`backend/uploads/`).
- Interview sessions are stored in server memory + JSON files.
- Register/login stores credentials hashed with bcrypt in PostgreSQL.
