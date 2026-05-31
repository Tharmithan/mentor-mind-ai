"""Study Agent — personal tutor: plans, revision, goals, daily recommendations (Week 6 · Day 2)."""

from __future__ import annotations

import re

from app.agents.study.goal_tracker import get_goal_tracker
from app.planner.generator import RoadmapGenerator
from app.planner.progress_store import get_plan_store
from app.agents.study.plan_generator import StudyPlanGenerator
from app.agents.study.revision_planner import RevisionPlanner, parse_revision_request
from app.agents.study.tutor_service import StudyTutorService
from app.agents.types import AgentType
from app.models.learning_planner import CreateLearningPlanRequest, LearningPlanProgressUpdate
from app.models.document import ChatRequest
from app.models.study_tools import StudyToolRequest
from app.models.study_tutor import LearningGoalUpdate, RevisionPlanRequest
from app.rag.document_service import DocumentService
from app.rag import study_tools as tools


async def run_study_agent(
    message: str,
    session_id: str | None,
    document_id: str | None,
    context: dict,
) -> dict:
    lower = message.lower()
    sid = session_id or context.get("agent_session_id") or "default"

    # --- Week 6 Day 5: personalized learning planner ---

    planner_req = RoadmapGenerator.parse_goal_from_message(message)
    if planner_req and re.search(
        r"\b(become|learning plan|learning planner|learning roadmap|path to|plan to become)\b",
        lower,
    ):
        roadmap = RoadmapGenerator.generate(planner_req)
        if re.search(r"\b(track|create plan|save|start plan|weekly)\b", lower):
            plan = get_plan_store().create(
                CreateLearningPlanRequest(
                    goal=planner_req.goal,
                    hours_per_week=planner_req.hours_per_week,
                )
            )
            weekly = get_plan_store().weekly_plan(plan.plan_id)
            answer = RoadmapGenerator.to_markdown(roadmap)
            if weekly:
                answer += "\n\n---\n\n" + weekly["weekly_markdown"]
            answer += f"\n\n_Plan ID: `{plan.plan_id}` — track progress via weekly updates._"
            return {
                "answer": answer,
                "used_llm": False,
                "sub_intent": "learning_plan",
                "data": {"plan_id": plan.plan_id, "roadmap": roadmap.model_dump()},
                "actions": [{"type": "navigate", "path": "/planner"}],
            }
        return {
            "answer": RoadmapGenerator.to_markdown(roadmap),
            "used_llm": False,
            "sub_intent": "learning_roadmap",
            "data": roadmap.model_dump(),
            "actions": [{"type": "navigate", "path": "/planner"}],
        }

    plan_id = context.get("learning_plan_id")
    if plan_id and re.search(r"\b(weekly plan|this week|complete milestone|progress)\b", lower):
        store = get_plan_store()
        if re.search(r"\b(complete|finished|done)\b.*\bmilestone\b", lower):
            plan = store.get(plan_id)
            if plan:
                pending = next((m for m in plan.milestones if not m.completed), None)
                if pending:
                    updated = store.update_progress(
                        plan_id,
                        LearningPlanProgressUpdate(milestone_id=pending.id),
                    )
                    if updated:
                        return {
                            "answer": f"**Milestone completed:** {pending.label}\n\nProgress: **{updated.progress_pct:.0f}%** · Now on Month {updated.current_month}",
                            "used_llm": False,
                            "sub_intent": "milestone_complete",
                            "data": updated.model_dump(),
                            "actions": [{"type": "navigate", "path": "/planner"}],
                        }
        weekly_data = store.weekly_plan(plan_id)
        if weekly_data:
            return {
                "answer": weekly_data["weekly_markdown"],
                "used_llm": False,
                "sub_intent": "weekly_plan",
                "data": weekly_data,
                "actions": [{"type": "navigate", "path": "/planner"}],
            }

    # --- Week 6 Day 2: personal tutor capabilities ---

    if re.search(
        r"\b(exam|study plan|prepare for|days until|day plan|\d+\s*days?\s*(?:until|left|to))\b",
        lower,
    ):
        plan = await StudyPlanGenerator.from_message(message)
        if plan:
            return {
                "answer": StudyPlanGenerator.to_markdown(plan),
                "used_llm": plan.used_llm,
                "sub_intent": "exam_plan",
                "data": {"study_plan": plan.model_dump()},
                "actions": [
                    {"type": "navigate", "path": "/dashboard"},
                    {"type": "open_study_tools", "tool": "revision"},
                ],
            }

    if re.search(r"\b(revision plan|revise|revision schedule|review plan)\b", lower):
        subject, days = parse_revision_request(message)
        rev = RevisionPlanner.build(
            RevisionPlanRequest(exam_subject=subject, days_until_exam=days)
        )
        return {
            "answer": RevisionPlanner.to_markdown(rev),
            "used_llm": False,
            "sub_intent": "revision_plan",
            "data": {"revision_plan": rev.model_dump()},
            "actions": [{"type": "open_study_tools", "tool": "revision"}],
        }

    tracker = get_goal_tracker()
    goal_create = tracker.parse_goal_from_message(message)
    if goal_create and re.search(r"\b(set|create|new|track|goal|want to learn)\b", lower):
        goal = tracker.create_goal(sid, goal_create)
        return {
            "answer": (
                f"**Learning goal tracked:** {goal.title}\n\n"
                f"• Subject: {goal.subject}\n"
                f"• Target: {goal.target_days} days\n"
                f"• Progress: {goal.progress_pct:.0f}%\n\n"
                "Say _\"I completed day 3\"_ or _\"Update progress to 40%\"_ to log milestones."
            ),
            "used_llm": False,
            "sub_intent": "goal_create",
            "data": {"goal": goal.model_dump()},
            "actions": [{"type": "navigate", "path": "/dashboard"}],
        }

    _, progress, milestone = tracker.parse_progress_update(message)
    if progress is not None or milestone:
        goals = tracker.list_goals(sid)
        if goals:
            target = goals[-1]
            updated = tracker.update_goal(
                sid,
                target.id,
                LearningGoalUpdate(progress_pct=progress, completed_milestone=milestone),
            )
            if updated:
                return {
                    "answer": (
                        f"**Progress updated** for _{updated.title}_\n\n"
                        f"• Progress: **{updated.progress_pct:.0f}%**\n"
                        f"• Milestones: {', '.join(updated.milestones_completed) or 'none yet'}"
                    ),
                    "used_llm": False,
                    "sub_intent": "goal_progress",
                    "data": {"goal": updated.model_dump()},
                    "actions": [{"type": "navigate", "path": "/dashboard"}],
                }

    if re.search(r"\b(my goals|show goals|goal progress|track progress)\b", lower):
        goals = tracker.list_goals(sid)
        if not goals:
            return {
                "answer": (
                    "No learning goals yet. Try:\n"
                    "_\"I want to learn Machine Learning in 30 days\"_"
                ),
                "used_llm": False,
                "sub_intent": "goal_list",
                "actions": [],
            }
        lines = [f"**Your learning goals** ({len(goals)})\n"]
        for g in goals:
            lines.append(f"• **{g.title}** — {g.progress_pct:.0f}% ({g.subject})")
        return {
            "answer": "\n".join(lines),
            "used_llm": False,
            "sub_intent": "goal_list",
            "data": {"goals": [g.model_dump() for g in goals]},
            "actions": [{"type": "navigate", "path": "/dashboard"}],
        }

    if re.search(r"\b(weak subject|weakest|struggling|weak area|analyze my)\b", lower):
        weak = StudyTutorService.analyze_weak_subjects()
        return {
            "answer": StudyTutorService.format_weak_subjects_markdown(weak),
            "used_llm": False,
            "sub_intent": "weak_subjects",
            "data": {"weak_subjects": [w.model_dump() for w in weak]},
            "actions": [{"type": "navigate", "path": "/dashboard"}],
        }

    if re.search(
        r"\b(daily|today|recommend|what should i study|study today|focus today)\b",
        lower,
    ):
        daily = StudyTutorService.daily_recommendations()
        return {
            "answer": StudyTutorService.format_daily_markdown(daily),
            "used_llm": False,
            "sub_intent": "daily_recommendations",
            "data": daily.model_dump(),
            "actions": [{"type": "navigate", "path": "/dashboard"}],
        }

    # --- Week 6 Day 1: learning tools ---

    if re.search(r"\b(quiz|mcq|test me)\b", lower):
        req = StudyToolRequest(document_id=document_id, topic=message, count=5)
        result = await tools.generate_quiz(req)
        answer = f"**Quiz ready** ({len(result.questions)} questions)\n\n"
        for i, q in enumerate(result.questions[:3], 1):
            answer += f"{i}. {q.question}\n"
        if len(result.questions) > 3:
            answer += f"\n…and {len(result.questions) - 3} more. Open **Study Tools** for the full quiz."
        return {
            "answer": answer,
            "used_llm": result.used_llm,
            "sub_intent": "quiz",
            "actions": [{"type": "open_study_tools", "tool": "quiz"}],
        }

    if re.search(r"\b(flashcard|flash card)\b", lower):
        req = StudyToolRequest(document_id=document_id, topic=message, count=6)
        result = await tools.generate_flashcards(req)
        lines = [f"• **{c.front}** → {c.back}" for c in result.flashcards[:4]]
        answer = "**Flashcards**\n\n" + "\n".join(lines)
        return {
            "answer": answer,
            "used_llm": result.used_llm,
            "sub_intent": "flashcards",
            "actions": [{"type": "open_study_tools", "tool": "flashcards"}],
        }

    if re.search(r"\b(summarize|summary|summarise)\b", lower):
        req = StudyToolRequest(document_id=document_id, topic=message)
        result = await tools.summarize(req)
        pts = "\n".join(f"• {p}" for p in result.key_points[:5])
        answer = f"**{result.title}**\n\n{result.summary}\n\n{pts}"
        return {
            "answer": answer,
            "used_llm": result.used_llm,
            "sub_intent": "summarize",
            "actions": [{"type": "open_study_tools", "tool": "summarize"}],
        }

    if re.search(r"\b(explain|simple|beginner|eli5)\b", lower):
        concept = re.sub(r"(?i)explain|simply|like a beginner|eli5", "", message).strip() or message
        result = await tools.explain_simple(concept, document_id=document_id)
        answer = f"**{result.concept}**\n\n{result.explanation}"
        if result.analogy:
            answer += f"\n\n_Analogy: {result.analogy}_"
        return {
            "answer": answer,
            "used_llm": result.used_llm,
            "sub_intent": "explain",
            "actions": [{"type": "open_study_tools", "tool": "explain"}],
        }

    if re.search(r"\b(revision sheet|revision mode|last.?minute|cram)\b", lower):
        req = StudyToolRequest(document_id=document_id, topic=message)
        result = await tools.revision_mode(req)
        notes = "\n".join(f"• {n}" for n in result.quick_notes[:5])
        answer = f"**{result.title}**\n\n{notes}"
        return {
            "answer": answer,
            "used_llm": result.used_llm,
            "sub_intent": "revision_sheet",
            "actions": [{"type": "open_study_tools", "tool": "revision"}],
        }

    # Default: RAG document chat
    mode = None
    if "example" in lower:
        mode = "example"
    elif "summarize" in lower:
        mode = "summarize"

    chat_req = ChatRequest(
        question=message,
        document_id=document_id or context.get("document_id"),
        session_id=session_id,
        mode=mode,
    )
    result = await DocumentService.chat(chat_req)
    src = ""
    if result.sources:
        src = "\n\n_Sources: " + ", ".join(s.filename for s in result.sources[:2]) + "_"
    return {
        "answer": result.answer + src,
        "used_llm": result.used_llm,
        "sub_intent": "document_qa",
        "sources": [s.model_dump() for s in result.sources[:3]],
        "actions": [{"type": "open_assistant", "tab": "chat"}],
    }


STUDY_AGENT = AgentType.STUDY
