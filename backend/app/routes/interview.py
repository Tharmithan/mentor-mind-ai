"""AI Interview Coach routes (Week 5 · Days 1–3).

    GET  /api/interview/types                    list HR / Technical / Behavioral
    GET  /api/interview/transcribe/status        Whisper availability
    POST /api/interview/transcribe               upload audio → transcript
    POST /api/interview/start                    start session → first question
    GET  /api/interview/session/{id}             session state + history
    POST /api/interview/session/{id}/answer      submit answer → AI evaluation
"""

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.interview.service import InterviewService
from app.models.interview import (
    InterviewSessionResponse,
    InterviewTypeInfo,
    StartInterviewRequest,
    StartInterviewResponse,
    SubmitAnswerRequest,
    SubmitAnswerResponse,
    TranscribeResponse,
    TranscribeStatusResponse,
)

router = APIRouter(prefix="/interview", tags=["interview"])


@router.get("/types", response_model=list[InterviewTypeInfo])
async def list_interview_types() -> list[InterviewTypeInfo]:
    return InterviewService.list_types()


@router.get("/transcribe/status", response_model=TranscribeStatusResponse)
async def transcribe_status() -> TranscribeStatusResponse:
    return InterviewService.transcribe_status()


@router.post("/transcribe", response_model=TranscribeResponse)
async def transcribe_audio(file: UploadFile = File(...)) -> TranscribeResponse:
    try:
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Empty audio file")
        return InterviewService.transcribe_audio(content, file.filename or "recording.webm")
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {exc}") from exc


@router.post("/start", response_model=StartInterviewResponse)
async def start_interview(body: StartInterviewRequest) -> StartInterviewResponse:
    try:
        return InterviewService.start(body.interview_type, body.num_questions)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/session/{session_id}", response_model=InterviewSessionResponse)
async def get_session(session_id: str) -> InterviewSessionResponse:
    try:
        return InterviewService.get_session(session_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/session/{session_id}/answer", response_model=SubmitAnswerResponse)
async def submit_answer(
    session_id: str, body: SubmitAnswerRequest
) -> SubmitAnswerResponse:
    try:
        text = body.transcript or body.answer_text
        return await InterviewService.submit_answer(session_id, text)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
