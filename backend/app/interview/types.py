"""Interview type definitions (Week 5 · Day 1)."""

from enum import Enum


class InterviewType(str, Enum):
    HR = "hr"
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"


INTERVIEW_TYPE_META: dict[str, dict] = {
    InterviewType.HR: {
        "id": "hr",
        "label": "HR Interview",
        "description": "Introduction, strengths, motivation, and culture fit.",
        "examples": ["Tell me about yourself", "Strengths & weaknesses"],
        "icon": "users",
    },
    InterviewType.TECHNICAL: {
        "id": "technical",
        "label": "Technical Interview",
        "description": "DSA, AI/ML, and web development fundamentals.",
        "examples": ["Data structures", "REST APIs", "ML concepts"],
        "icon": "code",
    },
    InterviewType.BEHAVIORAL: {
        "id": "behavioral",
        "label": "Behavioral Interview",
        "description": "Teamwork, leadership, conflict, and growth stories (STAR method).",
        "examples": ["Team projects", "Conflict resolution", "Leadership"],
        "icon": "message-circle",
    },
}
