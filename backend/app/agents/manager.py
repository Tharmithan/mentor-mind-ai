"""Agent Manager — orchestrates routing, memory, and agent execution (Week 6 · Day 1).

Flow:
  User message → Agent Router → Specialist Agent → Action + Response
                      ↑
                 Agent Memory
"""

from __future__ import annotations

from app.agents.memory import get_agent_memory
from app.agents.registry import ensure_registry, get_handler, list_agents
from app.agents.router import route_message
from app.agents.types import AGENT_META, AgentType
from app.models.agent import AgentChatRequest, AgentChatResponse, AgentInfo


class AgentManager:
    @staticmethod
    def list_agents() -> list[AgentInfo]:
        ensure_registry()
        return [AgentInfo(**a) for a in list_agents()]

    @staticmethod
    async def chat(req: AgentChatRequest) -> AgentChatResponse:
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
        session.add_assistant(answer, decision.agent.value)
        if result.get("data"):
            session.context.update(result["data"])
        store.save(session)
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
