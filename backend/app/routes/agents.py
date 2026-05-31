"""AI Agent routes (Week 6 · Day 1 + Day 6).

    GET  /api/agents/types           list Study / Interview / Career / Resume agents
    POST /api/agents/chat            route message → specialist agent → response + actions
    POST /api/agents/collaborate     multi-agent pipeline → unified response
    GET  /api/agents/session/{id}    agent session memory + routing history
"""

from fastapi import APIRouter, HTTPException

from app.agents.manager import AgentManager
from app.models.agent import (
    AgentChatRequest,
    AgentChatResponse,
    AgentInfo,
    AgentSessionResponse,
)

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("/types", response_model=list[AgentInfo])
async def list_agents() -> list[AgentInfo]:
    return AgentManager.list_agents()


@router.post("/chat", response_model=AgentChatResponse)
async def agent_chat(body: AgentChatRequest) -> AgentChatResponse:
    try:
        return await AgentManager.chat(body)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Agent error: {exc}") from exc


@router.post("/collaborate", response_model=AgentChatResponse)
async def agent_collaborate(body: AgentChatRequest) -> AgentChatResponse:
    """Run Career → Study → Interview → Resume pipeline with shared memory."""
    try:
        req = body.model_copy(update={"collaborate": True})
        return await AgentManager.collaborate(req)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Collaboration error: {exc}") from exc


@router.get("/session/{session_id}", response_model=AgentSessionResponse)
async def get_agent_session(session_id: str) -> AgentSessionResponse:
    data = AgentManager.get_session(session_id)
    if data is None:
        raise HTTPException(status_code=404, detail="Agent session not found")
    return AgentSessionResponse(**data)
