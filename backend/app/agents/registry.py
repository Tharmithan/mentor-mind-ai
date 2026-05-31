"""Agent registry — maps agent types to handlers (Week 6 · Day 1)."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from app.agents.types import AGENT_META, AgentType

AgentHandler = Callable[..., Awaitable[dict[str, Any]]]

_registry: dict[AgentType, AgentHandler] = {}


def register(agent: AgentType, handler: AgentHandler) -> None:
    _registry[agent] = handler


def get_handler(agent: AgentType) -> AgentHandler | None:
    return _registry.get(agent)


def list_agents() -> list[dict]:
    return [
        {"id": agent.value, **AGENT_META[agent.value]}
        for agent in AgentType
    ]


def _bootstrap() -> None:
    if _registry:
        return
    from app.agents.career_agent import run_career_agent
    from app.agents.interview_agent import run_interview_agent
    from app.agents.resume_agent import run_resume_agent
    from app.agents.study_agent import run_study_agent

    async def study_wrapper(**kwargs: Any) -> dict:
        return await run_study_agent(
            kwargs["message"],
            kwargs.get("session_id"),
            kwargs.get("document_id"),
            kwargs.get("context") or {},
        )

    async def interview_wrapper(**kwargs: Any) -> dict:
        return await run_interview_agent(
            kwargs["message"],
            kwargs.get("session_id"),
            kwargs.get("interview_session_id"),
            kwargs.get("context") or {},
        )

    async def career_wrapper(**kwargs: Any) -> dict:
        return await run_career_agent(kwargs["message"], kwargs.get("context") or {})

    async def resume_wrapper(**kwargs: Any) -> dict:
        return await run_resume_agent(kwargs["message"], kwargs.get("resume_text"))

    register(AgentType.STUDY, study_wrapper)
    register(AgentType.INTERVIEW, interview_wrapper)
    register(AgentType.CAREER, career_wrapper)
    register(AgentType.RESUME, resume_wrapper)


def ensure_registry() -> None:
    _bootstrap()
