"""Interview service layer (Week 5 · Days 1–4)."""

from pathlib import Path

from app.interview.fer_detector import analyze_frame_bytes, fer_model_available, opencv_available
from app.interview.feedback_generator import generate_coach_report
from app.interview.question_bank import get_question_bank
from app.interview.transcription import transcribe_bytes, whisper_available
from app.interview.session import get_session_store
from app.interview.types import INTERVIEW_TYPE_META, InterviewType
from app.models.interview import (
    CoachReport,
    EmotionAnalyzeResponse,
    EmotionStatusResponse,
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


def _coach_report_from_dict(data: dict | None) -> CoachReport | None:
    if not data:
        return None
    return CoachReport(**data)


def _summary_from_dict(data: dict | None) -> InterviewSummary | None:
    if not data:
        return None
    payload = dict(data)
    coach = payload.pop("coach_report", None)
    if coach:
        payload["coach_report"] = CoachReport(**coach)
    return InterviewSummary(**payload)


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
    async def submit_answer(
        session_id: str,
        answer_text: str,
        emotion_metrics: dict | None = None,
    ) -> SubmitAnswerResponse:
        store = get_session_store()
        session = store.get(session_id)
        if session is None:
            raise KeyError("Session not found")
        if session.is_complete:
            raise ValueError("Interview already completed")

        text = answer_text.strip()
        result = await session.submit_answer(text, emotion_metrics=emotion_metrics)
        store.save(session)

        turn = TurnFeedback(**result["turn"])
        next_q = (
            InterviewQuestionOut(**result["next_question"])
            if result.get("next_question")
            else None
        )
        summary = _summary_from_dict(result.get("summary"))
        coach = _coach_report_from_dict(result.get("coach_report"))
        return SubmitAnswerResponse(
            session_id=session_id,
            status=session.status.value,
            turn=turn,
            completed=result["completed"],
            next_question=next_q,
            summary=summary,
            coach_report=coach,
        )

    @staticmethod
    def get_session(session_id: str) -> InterviewSessionResponse:
        session = get_session_store().get(session_id)
        if session is None:
            raise KeyError("Session not found")
        data = session.to_dict()
        cq = data.get("current_question")
        summary = _summary_from_dict(data.get("summary"))
        return InterviewSessionResponse(
            session_id=data["session_id"],
            interview_type=data["interview_type"],
            status=data["status"],
            current_index=data["current_index"],
            total_questions=data["total_questions"],
            current_question=InterviewQuestionOut(**cq) if cq else None,
            turns=[TurnFeedback(**t) for t in data["turns"]],
            summary=summary,
            coach_report=_coach_report_from_dict(data.get("coach_report"))
            or (summary.coach_report if summary else None),
            created_at=data["created_at"],
            completed_at=data.get("completed_at"),
        )

    @staticmethod
    async def get_coach_report(session_id: str) -> CoachReport:
        store = get_session_store()
        session = store.get(session_id)
        if session is None:
            raise KeyError("Session not found")
        if not session.is_complete:
            raise ValueError("Interview not completed yet")
        if not session.coach_report:
            session.coach_report = await generate_coach_report(session)
            store.save(session)
        return CoachReport(**session.coach_report)

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

    @staticmethod
    def emotion_status() -> EmotionStatusResponse:
        ok_cv = opencv_available()
        ok_fer = fer_model_available()
        note = (
            "OpenCV + FER+ ready — POST a frame to /api/interview/emotion/analyze"
            if ok_fer
            else "Install opencv-python-headless; FER model downloads on first analyze."
            if ok_cv
            else "pip install -r requirements-interview.txt"
        )
        return EmotionStatusResponse(
            opencv_available=ok_cv,
            fer_model_available=ok_fer,
            note=note,
        )

    @staticmethod
    def analyze_emotion_frame(content: bytes) -> EmotionAnalyzeResponse:
        result = analyze_frame_bytes(content)
        return EmotionAnalyzeResponse(
            face_detected=result.get("face_detected", False),
            dominant_emotion=result.get("dominant_emotion", "neutral"),
            confidence=float(result.get("confidence", 50)),
            stress=float(result.get("stress", 40)),
            nervousness=float(result.get("nervousness", 40)),
            engagement=float(result.get("engagement", 40)),
            smile=float(result.get("smile", 0)),
            attention=float(result.get("attention", 50)),
            eye_contact=float(result.get("eye_contact", 50)),
            emotions=result.get("emotions", {}),
            model=result.get("model", "ferplus-onnx"),
            note=result.get("note"),
        )
