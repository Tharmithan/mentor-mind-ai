"""Multi-agent orchestrator — Career → Study → Interview → Resume (Week 6 · Day 6)."""

from __future__ import annotations

import re

from app.agents.career.profile_builder import ProfileBuilder
from app.agents.career.recommendation_engine import CareerRecommendationEngine
from app.agents.career.skill_gap import SkillGapAnalyzer
from app.agents.collaboration.shared_memory import SharedMemory
from app.agents.memory import AgentSession
from app.agents.types import AGENT_META, AgentType
from app.models.agent import AgentContribution
from app.models.career import CareerAnalysisRequest
from app.models.learning_planner import LearningRoadmapRequest
from app.planner.generator import RoadmapGenerator
# Interview question banks per career (collaboration shortcut)
CAREER_INTERVIEW_QUESTIONS: dict[str, list[str]] = {
    "ai_engineer": [
        "Explain the difference between fine-tuning and RAG for LLM applications.",
        "How would you design an AI feature with evaluation metrics and guardrails?",
        "Walk me through a deep learning project you built and the tradeoffs you made.",
        "How do you handle model latency and cost in production?",
        "Describe how you would debug a model that performs well offline but poorly live.",
    ],
    "data_scientist": [
        "How do you choose between precision and recall for an imbalanced dataset?",
        "Explain a time you communicated complex findings to non-technical stakeholders.",
        "Walk through your approach to feature engineering for a prediction problem.",
        "How do you detect and handle data leakage?",
        "Describe an A/B test you designed and how you interpreted the results.",
    ],
    "mlops_engineer": [
        "How would you set up a CI/CD pipeline for a machine learning model?",
        "Explain model monitoring and what you'd alert on in production.",
        "How do Docker and Kubernetes help ML deployment?",
        "Describe your experience with experiment tracking and model registries.",
        "How do you roll back a bad model deployment safely?",
    ],
    "software_engineer": [
        "Explain time complexity of your favorite sorting algorithm.",
        "Design a URL shortener — what components would you need?",
        "Tell me about a bug you found and how you fixed it.",
        "How do you approach code reviews and testing?",
        "Describe a system you built and how you handled scale.",
    ],
}

RESUME_PROJECTS: dict[str, list[str]] = {
    "ai_engineer": [
        "RAG chatbot over your notes with evaluation metrics (faithfulness, latency)",
        "Fine-tuned classifier with Hugging Face + FastAPI deploy",
        "Multi-agent assistant (like MentorMind) with tool use and memory",
    ],
    "data_scientist": [
        "End-to-end Kaggle project with EDA notebook + model card",
        "A/B test analysis dashboard with business recommendations",
        "Customer churn prediction with SHAP explainability write-up",
    ],
    "mlops_engineer": [
        "ML pipeline: train → MLflow → Docker → GitHub Actions deploy",
        "Model monitoring demo with drift detection alerts",
        "Kubernetes deployment of a scikit-learn API with health checks",
    ],
    "software_engineer": [
        "Full-stack app with auth, tests, and CI (React + FastAPI)",
        "Open-source contribution with meaningful PR merged",
        "System design doc + working prototype for a real problem",
    ],
}

STUDY_FOCUS_BY_CAREER: dict[str, list[str]] = {
    "ai_engineer": ["Deep Learning", "NLP", "LLM/RAG", "Python", "MLOps basics"],
    "data_scientist": ["Statistics", "Machine Learning", "SQL", "Data Visualization"],
    "mlops_engineer": ["Docker", "CI/CD", "Python", "Cloud", "ML pipelines"],
    "software_engineer": ["Data Structures", "Algorithms", "System Design", "APIs"],
}


def should_collaborate(message: str) -> bool:
    lower = message.lower()
    return bool(
        re.search(
            r"\b(full prep|complete plan|all agents|collaborate|multi.?agent|"
            r"prepare me for|help me become|get ready for|career prep|"
            r"everything i need|study.*interview.*resume)\b",
            lower,
        )
        or (
            re.search(r"\b(become|want to be|target role)\b", lower)
            and re.search(r"\b(ai engineer|data scientist|mlops|software engineer)\b", lower)
            and re.search(r"\b(prep|prepare|plan|help|guide|roadmap)\b", lower)
        )
    )


class AgentOrchestrator:
    @staticmethod
    async def run(
        message: str,
        session: AgentSession,
        resume_text: str | None = None,
    ) -> tuple[str, list[AgentContribution], list[dict], list[dict]]:
        """Run multi-agent pipeline; return unified answer, contributions, log, actions."""
        shared = SharedMemory(session)
        contributions: list[AgentContribution] = []
        log: list[dict] = []
        actions: list[dict] = []

        profile = ProfileBuilder.build(
            message=message,
            interview_session_id=session.context.get("interview_session_id"),
        )
        career_req = CareerAnalysisRequest(
            subject_scores=profile.subject_scores,
            interview_session_id=session.context.get("interview_session_id"),
        )

        # ── 1. Career Agent ──────────────────────────────────────────────
        career = await CareerRecommendationEngine.from_request(career_req, message)
        career_id = career.top_career.career_id
        shared.set("career_goal", career.top_career.title)
        shared.set("career_id", career_id)
        shared.set("match_score", career.top_career.match_score)

        gaps = SkillGapAnalyzer.analyze(profile, career_id)
        gap_skills = [g.skill for g in gaps.gaps[:4]]
        shared.set("skill_gaps", gap_skills)

        career_summary = (
            f"**{career.top_career.title}** is your best fit ({career.top_career.match_score:.0f}% match). "
            f"Top gaps: {', '.join(gap_skills[:3]) or 'none critical'}."
        )
        contributions.append(
            AgentContribution(
                agent=AgentType.CAREER.value,
                agent_label=AGENT_META[AgentType.CAREER.value]["label"],
                summary=career_summary,
                sub_intent="career_recommendation",
                data={"top_career": career.top_career.model_dump(), "gaps": gap_skills},
            )
        )
        log.append({"step": 1, "agent": "career", "action": "recommend_career", "output": career.top_career.title})
        shared.post_message("career", "study", f"User targets {career.top_career.title}. Focus on: {', '.join(gap_skills[:2])}")
        actions.append({"type": "navigate", "path": "/dashboard"})

        # ── 2. Study Agent ───────────────────────────────────────────────
        study_topics = STUDY_FOCUS_BY_CAREER.get(career_id, ["Python", "Machine Learning"])
        if gap_skills:
            study_topics = list(dict.fromkeys(gap_skills[:2] + study_topics))[:4]
        shared.set("study_focus", study_topics)

        roadmap = RoadmapGenerator.generate(
            LearningRoadmapRequest(goal=f"Become a {career.top_career.title}", hours_per_week=10)
        )
        month1 = roadmap.months[0] if roadmap.months else None
        month1_topics = ", ".join(t.name for t in month1.topics) if month1 else ", ".join(study_topics)

        study_summary = (
            f"Prioritize **{', '.join(study_topics[:3])}**. "
            f"Month 1 focus: {month1_topics}. "
            f"Recommend **Deep Learning** and **{study_topics[0]}** for {career.top_career.title} roles."
        )
        contributions.append(
            AgentContribution(
                agent=AgentType.STUDY.value,
                agent_label=AGENT_META[AgentType.STUDY.value]["label"],
                summary=study_summary,
                sub_intent="study_recommendations",
                data={"study_focus": study_topics, "month1": month1_topics},
            )
        )
        log.append({"step": 2, "agent": "study", "action": "recommend_topics", "output": study_topics})
        shared.post_message("study", "interview", f"User should study {', '.join(study_topics[:2])} before interviews.")
        actions.append({"type": "navigate", "path": "/planner"})

        # ── 3. Interview Agent ───────────────────────────────────────────
        questions = CAREER_INTERVIEW_QUESTIONS.get(career_id, CAREER_INTERVIEW_QUESTIONS["ai_engineer"])
        shared.set("interview_topics", questions[:5])

        interview_summary = (
            f"Practice these **{career.top_career.title}** interview questions:\n"
            + "\n".join(f"• {q}" for q in questions[:3])
            + (f"\n…and {len(questions) - 3} more in Mock Interview." if len(questions) > 3 else "")
        )
        contributions.append(
            AgentContribution(
                agent=AgentType.INTERVIEW.value,
                agent_label=AGENT_META[AgentType.INTERVIEW.value]["label"],
                summary=interview_summary,
                sub_intent="interview_questions",
                data={"questions": questions[:5]},
            )
        )
        log.append({"step": 3, "agent": "interview", "action": "generate_questions", "output": len(questions)})
        shared.post_message("interview", "resume", "User needs portfolio bullets aligned with interview stories.")
        actions.append({"type": "navigate", "path": "/interview"})

        # ── 4. Resume Agent ──────────────────────────────────────────────
        projects = RESUME_PROJECTS.get(career_id, RESUME_PROJECTS["ai_engineer"])
        resume_suggestions = [
            f"Add **{projects[0]}** with metrics (accuracy, latency, users)",
            f"Include keywords: {', '.join(study_topics[:3])}",
            "Quantify every bullet — % improvement, scale, or time saved",
        ]
        if gap_skills:
            resume_suggestions.insert(0, f"Highlight **{gap_skills[0]}** with a concrete project")
        shared.set("resume_suggestions", resume_suggestions)

        resume_summary = "**Resume additions:**\n" + "\n".join(f"• {s}" for s in resume_suggestions[:4])
        if resume_text:
            resume_summary += "\n\n_(Resume text provided — open Resume Analyzer for full ATS review.)_"
        contributions.append(
            AgentContribution(
                agent=AgentType.RESUME.value,
                agent_label=AGENT_META[AgentType.RESUME.value]["label"],
                summary=resume_summary,
                sub_intent="resume_projects",
                data={"projects": projects, "suggestions": resume_suggestions},
            )
        )
        log.append({"step": 4, "agent": "resume", "action": "suggest_projects", "output": projects[0]})
        actions.append({"type": "navigate", "path": "/resume"})

        unified = AgentOrchestrator.format_unified(message, contributions, shared)
        return unified, contributions, log, actions

    @staticmethod
    def format_unified(
        message: str,
        contributions: list[AgentContribution],
        shared: SharedMemory,
    ) -> str:
        goal = shared.get("career_goal", "your target role")
        lines = [
            f"## Multi-Agent Career Plan — {goal}\n",
            f"_Your request: \"{message[:120]}\"_\n",
            "Four specialists collaborated on this plan:\n",
        ]
        icons = {"career": "🎯", "study": "📚", "interview": "🎤", "resume": "📄"}
        for c in contributions:
            icon = icons.get(c.agent, "•")
            lines.append(f"### {icon} {c.agent_label}")
            lines.append(c.summary)
            lines.append("")
        lines.append("---")
        lines.append(
            "**Next steps:** Open the [Learning Planner](/planner), practice in [Mock Interview](/interview), "
            "and polish your resume in the [Resume Analyzer](/resume)."
        )
        return "\n".join(lines)
