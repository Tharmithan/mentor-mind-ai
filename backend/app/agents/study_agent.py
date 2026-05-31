"""Study Agent — document Q&A and learning tools (Week 6 · Day 1)."""

from __future__ import annotations

import re

from app.agents.types import AgentType
from app.models.document import ChatRequest
from app.models.study_tools import StudyToolRequest
from app.rag.document_service import DocumentService
from app.rag import study_tools as tools


async def run_study_agent(
    message: str,
    session_id: str | None,
    document_id: str | None,
    context: dict,
) -> dict:
    lower = message.lower()

    if re.search(r"\b(quiz|mcq|test me)\b", lower):
        req = StudyToolRequest(document_id=document_id, topic=message, count=5)
        result = await tools.generate_quiz(req)
        answer = f"**Quiz ready** ({len(result.questions)} questions)\n\n"
        for i, q in enumerate(result.questions[:3], 1):
            answer += f"{i}. {q.question}\n"
        if len(result.questions) > 3:
            answer += f"\n…and {len(result.questions) - 3} more. Open **Study Tools** for the full quiz."
        return {
            "answer": answer,
            "used_llm": result.used_llm,
            "sub_intent": "quiz",
            "actions": [{"type": "open_study_tools", "tool": "quiz"}],
        }

    if re.search(r"\b(flashcard|flash card)\b", lower):
        req = StudyToolRequest(document_id=document_id, topic=message, count=6)
        result = await tools.generate_flashcards(req)
        lines = [f"• **{c.front}** → {c.back}" for c in result.flashcards[:4]]
        answer = "**Flashcards**\n\n" + "\n".join(lines)
        return {
            "answer": answer,
            "used_llm": result.used_llm,
            "sub_intent": "flashcards",
            "actions": [{"type": "open_study_tools", "tool": "flashcards"}],
        }

    if re.search(r"\b(summarize|summary|summarise)\b", lower):
        req = StudyToolRequest(document_id=document_id, topic=message)
        result = await tools.summarize(req)
        pts = "\n".join(f"• {p}" for p in result.key_points[:5])
        answer = f"**{result.title}**\n\n{result.summary}\n\n{pts}"
        return {
            "answer": answer,
            "used_llm": result.used_llm,
            "sub_intent": "summarize",
            "actions": [{"type": "open_study_tools", "tool": "summarize"}],
        }

    if re.search(r"\b(explain|simple|beginner|eli5)\b", lower):
        concept = re.sub(r"(?i)explain|simply|like a beginner|eli5", "", message).strip() or message
        result = await tools.explain_simple(concept, document_id=document_id)
        answer = f"**{result.concept}**\n\n{result.explanation}"
        if result.analogy:
            answer += f"\n\n_Analogy: {result.analogy}_"
        return {
            "answer": answer,
            "used_llm": result.used_llm,
            "sub_intent": "explain",
            "actions": [{"type": "open_study_tools", "tool": "explain"}],
        }

    # Default: RAG document chat
    mode = None
    if "example" in lower:
        mode = "example"
    elif "summarize" in lower:
        mode = "summarize"

    chat_req = ChatRequest(
        question=message,
        document_id=document_id or context.get("document_id"),
        session_id=session_id,
        mode=mode,
    )
    result = await DocumentService.chat(chat_req)
    src = ""
    if result.sources:
        src = "\n\n_Sources: " + ", ".join(s.filename for s in result.sources[:2]) + "_"
    return {
        "answer": result.answer + src,
        "used_llm": result.used_llm,
        "sub_intent": "document_qa",
        "sources": [s.model_dump() for s in result.sources[:3]],
        "actions": [{"type": "open_assistant", "tab": "chat"}],
    }

STUDY_AGENT = AgentType.STUDY
