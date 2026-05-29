"""Pydantic models for AI Interview Coach API (Week 5 · Days 1–3)."""

from pydantic import BaseModel, Field


class InterviewTypeInfo(BaseModel):
    id: str
    label: str
    description: str
    examples: list[str]
    question_count: int


class InterviewQuestionOut(BaseModel):
    id: str
    text: str
    category: str
    difficulty: str
    tips: str
    interview_type: str


class StartInterviewRequest(BaseModel):
    interview_type: str = Field(description="hr | technical | behavioral")
    num_questions: int = Field(default=5, ge=1, le=10)


class SubmitAnswerRequest(BaseModel):
    answer_text: str = Field(min_length=1)
    # Day 2+: transcript from speech-to-text
    transcript: str | None = None


class EvaluationScores(BaseModel):
    communication: int
    technical_score: int
    confidence: int
    relevance: int
    grammar: int
    clarity: int
    keyword_match: int
    semantic_similarity: int
    answer_length: int
    overall: int


class IdealComparison(BaseModel):
    expert_answer: str
    expected_keywords: list[str]
    matched_keywords: list[str]
    missing_keywords: list[str]
    similarity_pct: float


class TurnFeedback(BaseModel):
    question_id: str
    question_text: str
    answer_text: str
    overall_score: float
    communication_score: float
    technical_score: float
    confidence_score: float
    feedback_summary: str
    strengths: list[str]
    improvements: list[str]
    scores: EvaluationScores | None = None
    ideal_comparison: IdealComparison | None = None
    used_llm: bool = False


class InterviewSummary(BaseModel):
    overall_score: float
    communication_score: float
    technical_score: float
    confidence_score: float
    questions_answered: int
    highlights: list[str]
    focus_areas: list[str]


class StartInterviewResponse(BaseModel):
    session_id: str
    interview_type: str
    status: str
    total_questions: int
    current_question: InterviewQuestionOut


class SubmitAnswerResponse(BaseModel):
    session_id: str
    status: str
    turn: TurnFeedback
    completed: bool
    next_question: InterviewQuestionOut | None = None
    summary: InterviewSummary | None = None


class TranscribeResponse(BaseModel):
    text: str
    language: str | None = None
    duration_sec: float | None = None
    whisper_available: bool = True


class TranscribeStatusResponse(BaseModel):
    whisper_available: bool
    model: str = "base"
    note: str = "Upload webm/wav/mp3 for Whisper transcription; use browser speech for live captions."


class InterviewSessionResponse(BaseModel):
    session_id: str
    interview_type: str
    status: str
    current_index: int
    total_questions: int
    current_question: InterviewQuestionOut | None = None
    turns: list[TurnFeedback]
    summary: InterviewSummary | None = None
    created_at: str
    completed_at: str | None = None
