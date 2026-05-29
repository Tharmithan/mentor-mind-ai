"""Smart Learning Features routes (Week 4 · Day 5).

    POST /api/study/summarize    AI summarizer
    POST /api/study/quiz         MCQ generator
    POST /api/study/flashcards   revision flashcards
    POST /api/study/explain      explain like a beginner
    POST /api/study/revision     exam revision mode
    GET  /api/study/status       whether the LLM is configured
"""

from fastapi import APIRouter, HTTPException

from app.models.study_tools import (
    ExplainSimpleRequest,
    ExplainSimpleResponse,
    FlashcardResponse,
    QuizResponse,
    RevisionResponse,
    StudyToolRequest,
    SummaryResponse,
)
from app.rag import study_tools as tools
from app.rag.llm import llm_enabled

router = APIRouter(prefix="/study", tags=["study-tools"])


@router.get("/status")
async def study_status() -> dict:
    return {
        "llm_enabled": llm_enabled(),
        "note": "Set OPENAI_API_KEY for AI-generated results; extractive fallback otherwise.",
    }


@router.post("/summarize", response_model=SummaryResponse)
async def summarize(body: StudyToolRequest) -> SummaryResponse:
    _require_source(body)
    return await tools.summarize(body)


@router.post("/quiz", response_model=QuizResponse)
async def quiz(body: StudyToolRequest) -> QuizResponse:
    _require_source(body)
    return await tools.generate_quiz(body)


@router.post("/flashcards", response_model=FlashcardResponse)
async def flashcards(body: StudyToolRequest) -> FlashcardResponse:
    _require_source(body)
    return await tools.generate_flashcards(body)


@router.post("/explain", response_model=ExplainSimpleResponse)
async def explain(body: ExplainSimpleRequest) -> ExplainSimpleResponse:
    return await tools.explain_simple(body.concept, document_id=body.document_id)


@router.post("/revision", response_model=RevisionResponse)
async def revision(body: StudyToolRequest) -> RevisionResponse:
    _require_source(body)
    return await tools.revision_mode(body)


def _require_source(body: StudyToolRequest) -> None:
    if not body.document_id and not body.topic:
        raise HTTPException(
            status_code=400,
            detail="Provide a document_id and/or a topic to generate from.",
        )
