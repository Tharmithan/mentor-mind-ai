"""Pydantic models for Smart Learning Features (Week 4 · Day 5).

Summarizer · Quiz Generator · Flashcards · Explain Like a Beginner · Exam Revision Mode.
"""

from pydantic import BaseModel, Field


class StudyToolRequest(BaseModel):
    """Source for a study tool: a whole document and/or a focused topic/query."""

    document_id: str | None = None
    topic: str | None = None
    count: int = Field(default=5, ge=1, le=15)


class SummaryResponse(BaseModel):
    title: str
    summary: str
    key_points: list[str]
    used_llm: bool
    source: str | None = None


class QuizQuestion(BaseModel):
    question: str
    options: list[str]
    answer_index: int
    explanation: str | None = None


class QuizResponse(BaseModel):
    questions: list[QuizQuestion]
    used_llm: bool
    source: str | None = None


class Flashcard(BaseModel):
    front: str
    back: str


class FlashcardResponse(BaseModel):
    flashcards: list[Flashcard]
    used_llm: bool
    source: str | None = None


class ExplainSimpleRequest(BaseModel):
    concept: str = Field(min_length=1)
    document_id: str | None = None


class ExplainSimpleResponse(BaseModel):
    concept: str
    explanation: str
    analogy: str | None = None
    used_llm: bool


class RevisionResponse(BaseModel):
    title: str
    quick_notes: list[str]
    key_formulas: list[str]
    must_know: list[str]
    used_llm: bool
    source: str | None = None
