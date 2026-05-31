"""Agent Manager — orchestrates routing, memory, and agent execution (Week 6 · Day 1).

Flow:
  User message → Agent Router → Specialist Agent → Action + Response
                      ↑
                 Agent Memory

Week 6 · Day 6 — multi-agent collaboration:
  User message → Orchestrator → Career → Study → Interview → Resume → Unified response
                      ↑
              Shared Memory (cross-agent workspace)
"""

from __future__ import annotations

from app.agents.collaboration import AgentOrchestrator, should_collaborate
from app.agents.memory import get_agent_memory
from app.agents.registry import ensure_registry, get_handler, list_agents
from app.agents.router import route_message
from app.agents.types import AGENT_META, AgentType
from app.models.agent import AgentChatRequest, AgentChatResponse, AgentInfo


def _resolve_user_id(session, req: AgentChatRequest) -> str:
    if req.context and req.context.get("user_id"):
        return str(req.context["user_id"])
    return str(session.context.get("user_id") or "demo-user-001")


def _persist_agent_memory(
    user_id: str,
    session_id: str,
    message: str,
    answer: str,
    agent: str,
) -> None:
    try:
        from app.memory.service import LongTermMemoryService

        LongTermMemoryService.record_agent_turn(user_id, session_id, message, answer, agent)
    except Exception:
        pass


def _enrich_with_progress(user_id: str, answer: str, agent: str) -> str:
    if agent not in ("study", "career", "orchestrator"):
        return answer
    try:
        from app.memory.service import LongTermMemoryService
        from app.personalization.store import get_profile_store

        profile = get_profile_store().get(user_id)
        scores = profile.subject_scores if profile else None
        prog = LongTermMemoryService.get_progress(user_id, scores)
        if prog.deltas:
            return f"> {prog.deltas[0].insight}\n\n{answer}"
    except Exception:
        pass
    return answer


class AgentManager:
    @staticmethod
    def list_agents() -> list[AgentInfo]:
        ensure_registry()
        return [AgentInfo(**a) for a in list_agents()]

    @staticmethod
    async def chat(req: AgentChatRequest) -> AgentChatResponse:
        if req.collaborate or should_collaborate(req.message):
            return await AgentManager.collaborate(req)
        return await AgentManager._single_agent_chat(req)

    @staticmethod
    async def collaborate(req: AgentChatRequest) -> AgentChatResponse:
        ensure_registry()
        store = get_agent_memory()
        session = store.get_or_create(req.session_id)

        if req.document_id:
            session.context["document_id"] = req.document_id
        if req.interview_session_id:
            session.context["interview_session_id"] = req.interview_session_id
        if req.context:
            session.context.update(req.context)

        session.add_user(req.message)

        answer, contributions, log, actions = await AgentOrchestrator.run(
            req.message,
            session,
            resume_text=req.resume_text,
        )

        user_id = _resolve_user_id(session, req)
        answer = _enrich_with_progress(user_id, answer, "orchestrator")
        session.add_assistant(answer, "orchestrator")
        session.context["last_collaboration"] = {
            "contributions": [c.model_dump() for c in contributions],
            "orchestration_log": log,
        }
        store.save(session)
        _persist_agent_memory(user_id, session.session_id, req.message, answer, "orchestrator")

        return AgentChatResponse(
            answer=answer,
            session_id=session.session_id,
            agent="orchestrator",
            agent_label="Multi-Agent Team",
            confidence=1.0,
            route_reason="Multi-agent collaboration pipeline (Career → Study → Interview → Resume)",
            sub_intent="multi_agent_collaboration",
            used_llm=False,
            actions=actions,
            collaboration=True,
            contributions=contributions,
            shared_memory=session.context.get("shared"),
            orchestration_log=log,
        )

    @staticmethod
    async def _single_agent_chat(req: AgentChatRequest) -> AgentChatResponse:
        ensure_registry()
        store = get_agent_memory()
        session = store.get_or_create(req.session_id)

        if req.document_id:
            session.context["document_id"] = req.document_id
        if req.interview_session_id:
            session.context["interview_session_id"] = req.interview_session_id
        if req.context:
            session.context.update(req.context)

        session.add_user(req.message)

        decision = await route_message(
            req.message,
            history=session.buffer_for_llm(),
            last_agent=session.last_agent,
        )
        session.log_route(decision.agent.value, decision.confidence, decision.reason)

        handler = get_handler(decision.agent)
        if handler is None:
            raise ValueError(f"No handler for agent: {decision.agent}")

        result = await handler(
            message=req.message,
            session_id=session.session_id,
            document_id=req.document_id or session.context.get("document_id"),
            interview_session_id=req.interview_session_id or session.context.get("interview_session_id"),
            resume_text=req.resume_text,
            context=session.context,
        )

        answer = result.get("answer", "I couldn't process that request.")
        user_id = _resolve_user_id(session, req)
        answer = _enrich_with_progress(user_id, answer, decision.agent.value)
        session.add_assistant(answer, decision.agent.value)
        if result.get("data"):
            session.context.update(result["data"])
        store.save(session)
        _persist_agent_memory(user_id, session.session_id, req.message, answer, decision.agent.value)
        return AgentChatResponse(
            answer=answer,
            session_id=session.session_id,
            agent=decision.agent.value,
            agent_label=AGENT_META[decision.agent.value]["label"],
            confidence=decision.confidence,
            route_reason=decision.reason,
            sub_intent=result.get("sub_intent"),
            used_llm=result.get("used_llm", False),
            actions=result.get("actions", []),
            sources=result.get("sources"),
        )

    @staticmethod
    def get_session(session_id: str) -> dict | None:
        session = get_agent_memory().get(session_id)
        return session.to_dict() if session else None
