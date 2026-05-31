"""Pydantic models for AI Interview Coach API (Week 5 · Days 1–5)."""

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


class EmotionMetricsIn(BaseModel):
    confidence: float = Field(ge=0, le=100)
    stress: float = Field(ge=0, le=100)
    nervousness: float = Field(ge=0, le=100)
    engagement: float = Field(ge=0, le=100)
    eye_contact: float = Field(ge=0, le=100)
    smile: float = Field(ge=0, le=100)
    attention: float = Field(ge=0, le=100)
    dominant_emotion: str = "neutral"
    samples: int = 1


class EmotionMetricsOut(BaseModel):
    confidence: float
    stress: float
    nervousness: float
    engagement: float
    eye_contact: float
    smile: float
    attention: float
    dominant_emotion: str
    samples: int
    delivery_tips: list[str] = []


class SubmitAnswerRequest(BaseModel):
    answer_text: str = Field(min_length=1)
    transcript: str | None = None
    emotion_metrics: EmotionMetricsIn | None = None


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
    human_feedback: list[str] = []
    weaknesses: list[str] = []
    improvement_suggestions: list[str] = []
    emotion_metrics: EmotionMetricsOut | None = None


class RoadmapPhase(BaseModel):
    phase: str
    focus: str
    actions: list[str]


class PracticeQuestion(BaseModel):
    question: str
    category: str
    reason: str


class CoachReport(BaseModel):
    overview: str
    strengths: list[str]
    weaknesses: list[str]
    improvement_roadmap: list[RoadmapPhase]
    learning_topics: list[str]
    practice_questions: list[PracticeQuestion]
    used_llm: bool = False


class InterviewSummary(BaseModel):
    overall_score: float
    communication_score: float
    technical_score: float
    confidence_score: float
    questions_answered: int
    highlights: list[str]
    focus_areas: list[str]
    coach_report: CoachReport | None = None


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
    coach_report: CoachReport | None = None


class EmotionAnalyzeResponse(BaseModel):
    face_detected: bool
    dominant_emotion: str
    confidence: float
    stress: float
    nervousness: float
    engagement: float
    smile: float
    attention: float
    eye_contact: float
    emotions: dict[str, float] = {}
    model: str = "ferplus-onnx"
    note: str | None = None


class EmotionStatusResponse(BaseModel):
    opencv_available: bool
    fer_model_available: bool
    model: str = "emotion-ferplus-8.onnx"
    note: str = "Upload a webcam frame (JPEG/PNG) for server-side FER analysis."


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
    coach_report: CoachReport | None = None
    created_at: str
    completed_at: str | None = None
