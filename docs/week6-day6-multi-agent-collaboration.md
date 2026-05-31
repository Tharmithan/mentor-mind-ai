# Week 6 · Day 6 — Multi-Agent Collaboration

**Goal:** Agents communicate with each other, share memory, and return one unified career prep plan.

---

## Example flow

```
User: "Help me become an AI Engineer — full career prep"
        ↓
Career Agent  → AI Engineer (87% match), skill gaps: Deep Learning, MLOps
        ↓ (shared memory)
Study Agent   → Recommend Deep Learning, Month 1 roadmap topics
        ↓
Interview Agent → Generate AI Engineer interview questions
        ↓
Resume Agent  → Suggest RAG chatbot + fine-tuning project bullets
        ↓
Unified markdown response + per-agent contribution cards
```

---

## Architecture

```
User message
     ↓
should_collaborate()  OR  collaborate=true
     ↓
AgentOrchestrator
     ├── SharedMemory (session.context["shared"])
     ├── Career  → career_goal, skill_gaps
     ├── Study   → study_focus (from gaps + roadmap)
     ├── Interview → interview_topics
     └── Resume  → resume_suggestions
     ↓
format_unified() → single answer + contributions[]
```

Single-agent chat still works via `POST /api/agents/chat` when collaboration is not triggered.

---

## Backend layout

```
backend/app/agents/collaboration/
├── shared_memory.py   # SharedMemory — cross-agent workspace + message log
├── orchestrator.py    # AgentOrchestrator, should_collaborate()
└── __init__.py

backend/app/agents/manager.py   # collaborate() + auto-detect in chat()
backend/app/models/agent.py     # AgentContribution, collaboration fields
backend/app/routes/agents.py    # POST /api/agents/collaborate
```

### Shared memory keys

| Key | Set by | Used by |
|-----|--------|---------|
| `career_goal` | Career | All downstream agents |
| `career_id` | Career | Study, Interview, Resume lookups |
| `skill_gaps` | Career | Study focus, Resume keywords |
| `study_focus` | Study | Resume keyword suggestions |
| `interview_topics` | Interview | User practice list |
| `resume_suggestions` | Resume | Final plan |
| `messages` | All | Inter-agent communication log |

---

## API

### Auto collaboration (via chat)

```http
POST /api/agents/chat
{
  "message": "Help me become an AI Engineer — full career prep"
}
```

Triggers when message matches collaboration patterns (`full prep`, `help me become`, `career prep`, etc.) or when `collaborate: true`.

### Explicit collaboration

```http
POST /api/agents/collaborate
{
  "message": "Prepare me for a data scientist role",
  "session_id": "abc123",
  "resume_text": "optional resume snippet"
}
```

### Response (extended)

```json
{
  "answer": "## Multi-Agent Career Plan — AI Engineer\n...",
  "agent": "orchestrator",
  "agent_label": "Multi-Agent Team",
  "collaboration": true,
  "contributions": [
    { "agent": "career", "agent_label": "Career Agent", "summary": "...", "sub_intent": "career_recommendation" },
    { "agent": "study", "agent_label": "Study Agent", "summary": "...", "sub_intent": "study_recommendations" },
    { "agent": "interview", "agent_label": "Interview Agent", "summary": "...", "sub_intent": "interview_questions" },
    { "agent": "resume", "agent_label": "Resume Agent", "summary": "...", "sub_intent": "resume_projects" }
  ],
  "shared_memory": { "career_goal": "AI Engineer", "skill_gaps": ["Deep Learning", "MLOps"], ... },
  "orchestration_log": [{ "step": 1, "agent": "career", "action": "recommend_career" }, ...],
  "actions": [{ "type": "navigate", "path": "/planner" }, ...]
}
```

---

## Frontend

- `FloatingAIAssistant` shows **Multi-Agent Team** badge and color-coded contribution cards per agent.
- Quick reply: *"Help me become an AI Engineer — full career prep"*
- `agentCollaborate()` in `frontend/src/lib/api.ts` for explicit pipeline calls.

---

## Smoke test

```bash
cd backend
python -c "
import asyncio
from app.agents.manager import AgentManager
from app.models.agent import AgentChatRequest

async def main():
    res = await AgentManager.collaborate(
        AgentChatRequest(message='Help me become an AI Engineer — full career prep')
    )
    assert res.collaboration
    assert len(res.contributions) == 4
    print('OK:', res.shared_memory['career_goal'])

asyncio.run(main())
"
```

---

## Collaboration triggers

Messages matching any of these patterns route to the multi-agent pipeline:

- `full prep`, `complete plan`, `career prep`, `prepare me for`
- `help me become` + role name + `prep/plan/guide`
- `study.*interview.*resume` (combined intent)
- Explicit `collaborate: true` on the request

---

## Next steps (Day 7+)

- LLM synthesis layer to merge agent summaries into a conversational tone
- Parallel agent execution where steps are independent
- User-selectable pipeline (e.g. Study + Interview only)
