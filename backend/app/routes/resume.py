"""Resume Analyzer routes (Week 6 · Day 4).

    POST /api/resume/upload          upload PDF → full analysis
    POST /api/resume/analyze         analyze pasted resume text
    GET  /api/resume/analysis/{id}   retrieve saved analysis
"""

from fastapi import APIRouter, File, HTTPException, Query, UploadFile

from app.models.resume import ResumeAnalysisResponse, ResumeTextAnalyzeRequest
from app.resume.analyzer import ResumeAnalyzer

router = APIRouter(prefix="/resume", tags=["resume-analyzer"])

ALLOWED = {".pdf", ".txt", ".md"}
MAX_BYTES = 10 * 1024 * 1024


@router.post("/upload", response_model=ResumeAnalysisResponse)
async def upload_resume(
    file: UploadFile = File(...),
    target_role: str | None = Query(default=None),
) -> ResumeAnalysisResponse:
    filename = file.filename or "resume.pdf"
    suffix = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if suffix not in ALLOWED:
        raise HTTPException(status_code=400, detail="Upload a PDF, TXT, or MD resume.")
    content = await file.read()
    if len(content) > MAX_BYTES:
        raise HTTPException(status_code=400, detail="File too large (max 10 MB).")
    if len(content) < 100:
        raise HTTPException(status_code=400, detail="File appears empty.")
    try:
        return await ResumeAnalyzer.analyze_upload(content, filename, target_role)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}") from exc


@router.post("/analyze", response_model=ResumeAnalysisResponse)
async def analyze_resume_text(body: ResumeTextAnalyzeRequest) -> ResumeAnalysisResponse:
    try:
        return await ResumeAnalyzer.analyze_text(body.text, target_role=body.target_role)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}") from exc


@router.get("/analysis/{analysis_id}", response_model=ResumeAnalysisResponse)
async def get_resume_analysis(analysis_id: str) -> ResumeAnalysisResponse:
    result = ResumeAnalyzer.get_analysis(analysis_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return result
