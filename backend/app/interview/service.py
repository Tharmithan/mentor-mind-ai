"""Interview service layer (Week 5 · Days 1–3)."""

from pathlib import Path

from app.interview.question_bank import get_question_bank
from app.interview.transcription import transcribe_bytes, whisper_available
from app.interview.session import get_session_store
from app.interview.types import INTERVIEW_TYPE_META, InterviewType
from app.models.interview import (
    InterviewQuestionOut,
    InterviewSessionResponse,
    InterviewSummary,
    InterviewTypeInfo,
    StartInterviewResponse,
    SubmitAnswerResponse,
    TranscribeResponse,
    TranscribeStatusResponse,
    TurnFeedback,
)


class InterviewService:
    @staticmethod
    def list_types() -> list[InterviewTypeInfo]:
        bank = get_question_bank()
        out: list[InterviewTypeInfo] = []
        for itype in InterviewType:
            meta = INTERVIEW_TYPE_META[itype]
            out.append(
                InterviewTypeInfo(
                    id=meta["id"],
                    label=meta["label"],
                    description=meta["description"],
                    examples=meta["examples"],
                    question_count=bank.count(itype.value),
                )
            )
        return out

    @staticmethod
    def start(interview_type: str, num_questions: int = 5) -> StartInterviewResponse:
        if interview_type not in {t.value for t in InterviewType}:
            raise ValueError(f"Invalid interview_type. Use: hr, technical, behavioral")
        session = get_session_store().create(interview_type, num_questions)
        q = session.current_question()
        assert q is not None
        return StartInterviewResponse(
            session_id=session.session_id,
            interview_type=session.interview_type,
            status=session.status.value,
            total_questions=session.total_questions,
            current_question=InterviewQuestionOut(**q.to_dict()),
        )

    @staticmethod
    async def submit_answer(session_id: str, answer_text: str) -> SubmitAnswerResponse:
        store = get_session_store()
        session = store.get(session_id)
        if session is None:
            raise KeyError("Session not found")
        if session.is_complete:
            raise ValueError("Interview already completed")

        text = answer_text.strip()
        result = await session.submit_answer(text)
        store.save(session)

        turn = TurnFeedback(**result["turn"])
        next_q = (
            InterviewQuestionOut(**result["next_question"])
            if result.get("next_question")
            else None
        )
        summary = (
            InterviewSummary(**result["summary"]) if result.get("summary") else None
        )
        return SubmitAnswerResponse(
            session_id=session_id,
            status=session.status.value,
            turn=turn,
            completed=result["completed"],
            next_question=next_q,
            summary=summary,
        )

    @staticmethod
    def get_session(session_id: str) -> InterviewSessionResponse:
        session = get_session_store().get(session_id)
        if session is None:
            raise KeyError("Session not found")
        data = session.to_dict()
        cq = data.get("current_question")
        return InterviewSessionResponse(
            session_id=data["session_id"],
            interview_type=data["interview_type"],
            status=data["status"],
            current_index=data["current_index"],
            total_questions=data["total_questions"],
            current_question=InterviewQuestionOut(**cq) if cq else None,
            turns=[TurnFeedback(**t) for t in data["turns"]],
            summary=InterviewSummary(**data["summary"]) if data.get("summary") else None,
            created_at=data["created_at"],
            completed_at=data.get("completed_at"),
        )

    @staticmethod
    def transcribe_status() -> TranscribeStatusResponse:
        ok = whisper_available()
        note = (
            "Whisper ready — upload audio for accurate transcription."
            if ok
            else "Install openai-whisper and ffmpeg; live captions still work in the browser."
        )
        return TranscribeStatusResponse(whisper_available=ok, note=note)

    @staticmethod
    def transcribe_audio(content: bytes, filename: str) -> TranscribeResponse:
        suffix = Path(filename).suffix or ".webm"
        if not whisper_available():
            raise RuntimeError(
                "Whisper not installed. pip install -r requirements-interview.txt && brew install ffmpeg"
            )
        result = transcribe_bytes(content, suffix=suffix)
        return TranscribeResponse(
            text=result["text"],
            language=result.get("language"),
            duration_sec=result.get("duration_sec"),
            whisper_available=True,
        )
