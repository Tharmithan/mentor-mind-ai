"""Interview session state machine (Week 5 · Day 1).

Flow:
  start → question_asked → answer_submitted → (feedback) → next question … → completed
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path

from app.interview.emotion_analyzer import delivery_tips
from app.interview.evaluator import evaluate_answer
from app.interview.feedback_generator import generate_coach_report, generate_turn_feedback
from app.interview.question_bank import InterviewQuestion, get_question_bank

SESSIONS_DIR = Path(__file__).resolve().parents[2] / "uploads" / "interview_sessions"


class SessionStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"


@dataclass
class TurnRecord:
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
    scores: dict | None = None
    ideal_comparison: dict | None = None
    used_llm: bool = False
    human_feedback: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)
    improvement_suggestions: list[str] = field(default_factory=list)
    emotion_metrics: dict | None = None

    def to_dict(self) -> dict:
        d = {
            "question_id": self.question_id,
            "question_text": self.question_text,
            "answer_text": self.answer_text,
            "overall_score": self.overall_score,
            "communication_score": self.communication_score,
            "technical_score": self.technical_score,
            "confidence_score": self.confidence_score,
            "feedback_summary": self.feedback_summary,
            "strengths": self.strengths,
            "improvements": self.improvements,
            "used_llm": self.used_llm,
            "human_feedback": self.human_feedback,
            "weaknesses": self.weaknesses,
            "improvement_suggestions": self.improvement_suggestions,
        }
        if self.scores:
            d["scores"] = self.scores
        if self.ideal_comparison:
            d["ideal_comparison"] = self.ideal_comparison
        if self.emotion_metrics:
            d["emotion_metrics"] = self.emotion_metrics
        return d


@dataclass
class InterviewSession:
    session_id: str
    interview_type: str
    status: SessionStatus = SessionStatus.ACTIVE
    questions: list[InterviewQuestion] = field(default_factory=list)
    current_index: int = 0
    turns: list[TurnRecord] = field(default_factory=list)
    coach_report: dict | None = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: str | None = None

    @property
    def total_questions(self) -> int:
        return len(self.questions)

    @property
    def is_complete(self) -> bool:
        return self.status == SessionStatus.COMPLETED

    def current_question(self) -> InterviewQuestion | None:
        if self.is_complete or self.current_index >= len(self.questions):
            return None
        return self.questions[self.current_index]

    async def submit_answer(
        self, answer_text: str, emotion_metrics: dict | None = None
    ) -> dict:
        """Evaluate answer (AI + heuristics), record turn, advance index."""
        q = self.current_question()
        if q is None:
            raise ValueError("No active question in this session.")

        analysis = await evaluate_answer(q, answer_text)
        feedback = await generate_turn_feedback(q, answer_text.strip(), analysis)

        emotion_out = None
        if emotion_metrics:
            tips = delivery_tips(emotion_metrics)
            emotion_out = {**emotion_metrics, "delivery_tips": tips}
            feedback["improvement_suggestions"] = list(
                dict.fromkeys(feedback.get("improvement_suggestions", []) + tips)
            )[:5]

        turn = TurnRecord(
            question_id=q.id,
            question_text=q.text,
            answer_text=answer_text.strip(),
            overall_score=analysis["overall_score"],
            communication_score=analysis["communication_score"],
            technical_score=analysis["technical_score"],
            confidence_score=analysis["confidence_score"],
            feedback_summary=analysis["feedback_summary"],
            strengths=feedback.get("strengths", analysis["strengths"]),
            improvements=analysis["improvements"],
            scores=analysis.get("scores"),
            ideal_comparison=analysis.get("ideal_comparison"),
            used_llm=analysis.get("used_llm", False) or feedback.get("used_llm", False),
            human_feedback=feedback.get("human_feedback", []),
            weaknesses=feedback.get("weaknesses", []),
            improvement_suggestions=feedback.get("improvement_suggestions", []),
            emotion_metrics=emotion_out,
        )
        self.turns.append(turn)
        self.current_index += 1

        if self.current_index >= len(self.questions):
            self.status = SessionStatus.COMPLETED
            self.completed_at = datetime.now(timezone.utc).isoformat()
            self.coach_report = await generate_coach_report(self)

        next_q = self.current_question()
        return {
            "turn": turn.to_dict(),
            "analysis": analysis,
            "completed": self.is_complete,
            "next_question": next_q.to_dict() if next_q else None,
            "summary": self.summary() if self.is_complete else None,
            "coach_report": self.coach_report,
        }

    def summary(self) -> dict | None:
        if not self.turns:
            return None
        n = len(self.turns)
        base = {
            "overall_score": round(sum(t.overall_score for t in self.turns) / n, 1),
            "communication_score": round(sum(t.communication_score for t in self.turns) / n, 1),
            "technical_score": round(sum(t.technical_score for t in self.turns) / n, 1),
            "confidence_score": round(sum(t.confidence_score for t in self.turns) / n, 1),
            "questions_answered": n,
            "highlights": [t.strengths[0] for t in self.turns if t.strengths][:3],
            "focus_areas": [t.improvements[0] for t in self.turns if t.improvements][:3],
        }
        if self.coach_report:
            base["coach_report"] = self.coach_report
        return base

    def to_dict(self) -> dict:
        cq = self.current_question()
        return {
            "session_id": self.session_id,
            "interview_type": self.interview_type,
            "status": self.status.value,
            "current_index": self.current_index,
            "total_questions": self.total_questions,
            "current_question": cq.to_dict() if cq else None,
            "turns": [t.to_dict() for t in self.turns],
            "summary": self.summary() if self.is_complete else None,
            "coach_report": self.coach_report,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "InterviewSession":
        bank = get_question_bank()
        questions = []
        for qid in data.get("question_ids", []):
            q = bank.get_by_id(qid)
            if q:
                questions.append(q)
        session = cls(
            session_id=data["session_id"],
            interview_type=data["interview_type"],
            status=SessionStatus(data.get("status", "active")),
            questions=questions,
            current_index=data.get("current_index", 0),
            created_at=data.get("created_at", ""),
            completed_at=data.get("completed_at"),
        )
        session.coach_report = data.get("coach_report")
        for t in data.get("turns", []):
            session.turns.append(
                TurnRecord(
                    question_id=t["question_id"],
                    question_text=t["question_text"],
                    answer_text=t["answer_text"],
                    overall_score=t["overall_score"],
                    communication_score=t["communication_score"],
                    technical_score=t["technical_score"],
                    confidence_score=t["confidence_score"],
                    feedback_summary=t["feedback_summary"],
                    strengths=t.get("strengths", []),
                    improvements=t.get("improvements", []),
                    scores=t.get("scores"),
                    ideal_comparison=t.get("ideal_comparison"),
                    used_llm=t.get("used_llm", False),
                    human_feedback=t.get("human_feedback", []),
                    weaknesses=t.get("weaknesses", []),
                    improvement_suggestions=t.get("improvement_suggestions", []),
                    emotion_metrics=t.get("emotion_metrics"),
                )
            )
        return session


class SessionStore:
    def __init__(self) -> None:
        self._cache: dict[str, InterviewSession] = {}
        SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

    def create(self, interview_type: str, num_questions: int = 5) -> InterviewSession:
        questions = get_question_bank().pick(interview_type, num_questions)
        session = InterviewSession(
            session_id=uuid.uuid4().hex[:12],
            interview_type=interview_type,
            questions=questions,
        )
        self._cache[session.session_id] = session
        self._persist(session)
        return session

    def get(self, session_id: str) -> InterviewSession | None:
        if session_id in self._cache:
            return self._cache[session_id]
        path = SESSIONS_DIR / f"{session_id}.json"
        if not path.exists():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        session = InterviewSession.from_dict(data)
        self._cache[session_id] = session
        return session

    def save(self, session: InterviewSession) -> None:
        self._cache[session.session_id] = session
        self._persist(session)

    def _persist(self, session: InterviewSession) -> None:
        payload = session.to_dict()
        payload["question_ids"] = [q.id for q in session.questions]
        (SESSIONS_DIR / f"{session.session_id}.json").write_text(
            json.dumps(payload, indent=2), encoding="utf-8"
        )


_store: SessionStore | None = None


def get_session_store() -> SessionStore:
    global _store
    if _store is None:
        _store = SessionStore()
    return _store
