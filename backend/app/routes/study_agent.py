"""Study Agent routes (Week 6 · Day 2).

    POST /api/agents/study/plan              exam study plan generator
    POST /api/agents/study/revision          revision planner
    GET  /api/agents/study/daily             daily study recommendations
    GET  /api/agents/study/weak-subjects     weak subject analysis
    GET  /api/agents/study/goals/{session}   list learning goals
    POST /api/agents/study/goals/{session}   create learning goal
    PATCH /api/agents/study/goals/{session}/{id}  update progress
"""

from fastapi import APIRouter, HTTPException

from app.agents.study.goal_tracker import get_goal_tracker
from app.agents.study.plan_generator import StudyPlanGenerator
from app.agents.study.revision_planner import RevisionPlanner
from app.agents.study.tutor_service import StudyTutorService
from app.models.study_tutor import (
    DailyStudyRecommendationsResponse,
    ExamStudyPlanRequest,
    ExamStudyPlanResponse,
    LearningGoal,
    LearningGoalCreate,
    LearningGoalUpdate,
    LearningGoalsResponse,
    RevisionPlanRequest,
    RevisionPlanResponse,
)

router = APIRouter(prefix="/agents/study", tags=["study-agent"])


@router.post("/plan", response_model=ExamStudyPlanResponse)
async def create_exam_plan(body: ExamStudyPlanRequest) -> ExamStudyPlanResponse:
    return await StudyPlanGenerator.generate(body)


@router.post("/revision", response_model=RevisionPlanResponse)
async def create_revision_plan(body: RevisionPlanRequest) -> RevisionPlanResponse:
    return RevisionPlanner.build(body)


@router.get("/daily", response_model=DailyStudyRecommendationsResponse)
async def daily_recommendations() -> DailyStudyRecommendationsResponse:
    return StudyTutorService.daily_recommendations()


@router.get("/weak-subjects")
async def weak_subjects() -> dict:
    weak = StudyTutorService.analyze_weak_subjects()
    return {
        "weak_subjects": [w.model_dump() for w in weak],
        "summary": StudyTutorService.format_weak_subjects_markdown(weak),
    }


@router.get("/goals/{session_id}", response_model=LearningGoalsResponse)
async def list_goals(session_id: str) -> LearningGoalsResponse:
    goals = get_goal_tracker().list_goals(session_id)
    return LearningGoalsResponse(session_id=session_id, goals=goals)


@router.post("/goals/{session_id}", response_model=LearningGoal)
async def create_goal(session_id: str, body: LearningGoalCreate) -> LearningGoal:
    return get_goal_tracker().create_goal(session_id, body)


@router.patch("/goals/{session_id}/{goal_id}", response_model=LearningGoal)
async def update_goal(
    session_id: str, goal_id: str, body: LearningGoalUpdate
) -> LearningGoal:
    updated = get_goal_tracker().update_goal(session_id, goal_id, body)
    if updated is None:
        raise HTTPException(status_code=404, detail="Goal not found")
    return updated
