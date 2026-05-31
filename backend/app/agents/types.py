"""Agent types and routing decisions (Week 6 · Day 1)."""

from __future__ import annotations

from enum import Enum


class AgentType(str, Enum):
    STUDY = "study"
    INTERVIEW = "interview"
    CAREER = "career"
    RESUME = "resume"


AGENT_META: dict[str, dict] = {
    AgentType.STUDY.value: {
        "label": "Study Agent",
        "description": "Personal tutor — exam plans, revision, goals, daily recommendations, document Q&A",
        "examples": [
            "I have a Machine Learning exam in 14 days",
            "What should I study today?",
            "Analyze my weak subjects",
        ],
    },
    AgentType.INTERVIEW.value: {
        "label": "Interview Agent",
        "description": "Mock interviews, coaching, HR/technical/behavioral prep",
        "examples": ["Start a technical interview", "How do I answer tell me about yourself?"],
    },
    AgentType.CAREER.value: {
        "label": "Career Agent",
        "description": "Career path recommendations, skill gaps, learning roadmaps, industry trends",
        "examples": [
            "Which career path fits me best?",
            "Skill gap analysis for Data Scientist",
            "Learning roadmap to become an AI Engineer",
        ],
    },
    AgentType.RESUME.value: {
        "label": "Resume Agent",
        "description": "PDF resume upload, ATS scoring, skill gaps, and AI feedback",
        "examples": [
            "Analyze my resume",
            "Upload my CV for ATS score",
            "Help me improve my resume bullet points",
        ],
    },
}


class RouteDecision:
    def __init__(
        self,
        agent: AgentType,
        confidence: float,
        reason: str,
        sub_intent: str | None = None,
    ) -> None:
        self.agent = agent
        self.confidence = confidence
        self.reason = reason
        self.sub_intent = sub_intent
