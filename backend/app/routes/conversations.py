"""Conversation memory routes (Week 4 · Day 6).

    POST   /api/chat/sessions        start a new conversation (returns session_id)
    GET    /api/chat/sessions/{id}   fetch a conversation's history + context
    DELETE /api/chat/sessions/{id}   forget a conversation
"""

from fastapi import APIRouter, HTTPException

from app.models.document import ChatMessage, ConversationResponse
from app.rag.memory import Session, get_memory

router = APIRouter(prefix="/chat", tags=["conversations"])


def _to_response(session: Session) -> ConversationResponse:
    return ConversationResponse(
        session_id=session.session_id,
        messages=[ChatMessage(**m) for m in session.buffer()],
        last_document_id=session.last_document_id,
        created_at=session.created_at,
        updated_at=session.updated_at,
    )


@router.post("/sessions", response_model=ConversationResponse)
async def create_session() -> ConversationResponse:
    return _to_response(get_memory().create())


@router.get("/sessions/{session_id}", response_model=ConversationResponse)
async def get_session(session_id: str) -> ConversationResponse:
    session = get_memory().get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return _to_response(session)


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str) -> dict:
    if not get_memory().delete(session_id):
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return {"message": "Conversation forgotten.", "session_id": session_id}
