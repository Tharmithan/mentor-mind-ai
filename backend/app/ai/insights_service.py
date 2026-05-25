from app.ai.insights_engine import InsightsEngine, StudentSnapshot, get_insights_engine
from app.ai.llm_insights import generate_llm_report
from app.models.insights import (
    AIInsight,
    InsightsReportResponse,
    InsightsRequest,
    InsightsResponse,
    PerformanceSummary,
)


class InsightsService:
    @staticmethod
    def _snapshot_from_request(req: InsightsRequest | None) -> StudentSnapshot:
        engine = get_insights_engine()
        if req is None:
            return engine.normalize_snapshot(None)

        scores = {s.subject: s.score for s in req.subject_scores} if req.subject_scores else {}
        prev_scores = (
            {s.subject: s.score for s in req.previous_subject_scores}
            if req.previous_subject_scores
            else {}
        )
        snap = StudentSnapshot(
            study_hours=req.study_hours,
            attendance_pct=req.attendance_pct,
            sleep_hours=req.sleep_hours,
            subject_scores=scores,
            previous_attendance_pct=req.previous_attendance_pct,
            previous_subject_scores=prev_scores,
        )
        return engine.normalize_snapshot(snap)

    @staticmethod
    def _to_response(payload: dict) -> InsightsResponse:
        return InsightsResponse(
            generated_at=payload["generated_at"],
            insights=[AIInsight(**i) for i in payload["insights"]],
            trends=[AIInsight(**i) for i in payload["trends"]],
            performance_summary=PerformanceSummary(**payload["performance_summary"]),
            cohort_stats=payload.get("cohort_stats", {}),
        )

    @staticmethod
    def generate(req: InsightsRequest | None = None) -> InsightsResponse:
        engine = get_insights_engine()
        snap = InsightsService._snapshot_from_request(req)
        payload = engine.generate_all(snap)
        return InsightsService._to_response(payload)

    @staticmethod
    async def generate_report(req: InsightsRequest | None = None) -> InsightsReportResponse:
        engine = get_insights_engine()
        snap = InsightsService._snapshot_from_request(req)
        payload = engine.generate_all(snap)

        llm_text = await generate_llm_report(payload)
        nl_report = engine.natural_language_report(payload, llm_text)
        engine.persist_results(payload, nl_report)

        return InsightsReportResponse(
            generated_at=payload["generated_at"],
            natural_language_report=nl_report,
            llm_enhanced=llm_text is not None,
            performance_summary=PerformanceSummary(**payload["performance_summary"]),
            insights=[AIInsight(**i) for i in payload["insights"]],
        )
