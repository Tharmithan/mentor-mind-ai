# Week 6 · Day 1 — AI Agent Architecture

**Goal:** Move from a single chatbot to a **multi-agent copilot** that routes user intent to specialist agents, remembers context, and returns actionable responses.

---

## Architecture

Instead of:

```
User → Chatbot → Response
```

We now have:

```
User
 ↓
Agent Router (keyword + optional LLM)
 ↓
 ├── Study Agent      — PDF Q&A, quiz, flashcards, explain
 ├── Interview Agent  — start mock interview, coaching tips, coach report
 ├── Career Agent     — insights, study planner, recommendations
 └── Resume Agent     — resume tips, bullet rewrites
        ↓
   Agent Memory (session turns + routing log)
        ↓
   Response + suggested actions
```

---

## Backend layout

```
backend/app/agents/
├── types.py           # AgentType enum, AGENT_META, RouteDecision
├── router.py          # route_message() — keyword rules + LLM fallback
├── registry.py        # handler registry + bootstrap
├── manager.py         # AgentManager.chat() orchestration
├── memory.py          # AgentSession store → uploads/agent_sessions/
├── study_agent.py
├── interview_agent.py
├── career_agent.py
└── resume_agent.py

backend/app/routes/agents.py
backend/app/models/agent.py
```

Sessions persist to `backend/uploads/agent_sessions/` (gitignored).

---

## API

| Method | Route | Description |
|--------|-------|-------------|
| `GET` | `/api/agents/types` | List Study / Interview / Career / Resume agents |
| `POST` | `/api/agents/chat` | Route message → specialist → answer + actions |
| `GET` | `/api/agents/session/{id}` | Session memory + routing history |

### Chat request

```json
{
  "message": "Start a technical mock interview",
  "session_id": "optional-continuity-id",
  "document_id": "optional-for-study-agent",
  "interview_session_id": "optional-for-coach-report",
  "resume_text": "optional-for-resume-agent"
}
```

### Chat response

```json
{
  "answer": "…",
  "session_id": "abc123",
  "agent": "interview",
  "agent_label": "Interview Coach",
  "confidence": 0.92,
  "route_reason": "keyword: mock interview",
  "actions": [{ "type": "open_interview", "path": "/interview" }]
}
```

---

## Routing

1. **Keyword rules** — fast path for study / interview / career / resume phrases.
2. **Last-agent bias** — follow-up messages stay with the same agent when ambiguous.
3. **LLM fallback** — when confidence is low and `OPENAI_API_KEY` is set, `call_llm` picks the best agent.

---

## Frontend

| Component | Role |
|-----------|------|
| `FloatingAIAssistant` | Global copilot widget → `POST /api/agents/chat` |
| `lib/api.ts` | `getAgentTypes()`, `agentChat()` |
| `lib/types/api.ts` | `AgentChatRequest`, `AgentChatResponse` |

The floating assistant shows which specialist answered, renders Markdown replies, and surfaces action links (e.g. open Interview page).

---

## Try it

```bash
# Backend
cd backend && uvicorn app.main:app --reload --port 8000

# List agents
curl -s http://127.0.0.1:8000/api/agents/types | jq

# Route a study question
curl -s -X POST http://127.0.0.1:8000/api/agents/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Explain neural networks simply"}' | jq

# Route interview intent
curl -s -X POST http://127.0.0.1:8000/api/agents/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Start a behavioral mock interview"}' | jq
```

Open the app → click the floating **MentorMind AI** button → ask a question.

---

## Next (Week 6 · Day 2+)

- Tool-use loop (agents call APIs autonomously)
- User profile + long-term memory
- Proactive nudges from dashboard / interview scores
- Unified chat panel with agent handoff UI
