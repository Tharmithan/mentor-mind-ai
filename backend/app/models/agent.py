"""Pydantic models for AI Agent API (Week 6 · Day 1)."""

from pydantic import BaseModel, Field


class AgentInfo(BaseModel):
    id: str
    label: str
    description: str
    examples: list[str]


class AgentChatRequest(BaseModel):
    message: str = Field(min_length=1)
    session_id: str | None = None
    document_id: str | None = None
    interview_session_id: str | None = None
    resume_text: str | None = None
    context: dict | None = None


class AgentAction(BaseModel):
    type: str
    path: str | None = None
    tool: str | None = None
    tab: str | None = None
    topic: str | None = None
    session_id: str | None = None


class AgentChatResponse(BaseModel):
    answer: str
    session_id: str
    agent: str
    agent_label: str
    confidence: float
    route_reason: str
    sub_intent: str | None = None
    used_llm: bool = False
    actions: list[dict] = Field(default_factory=list)
    sources: list[dict] | None = None


class AgentSessionResponse(BaseModel):
    session_id: str
    turns: list[dict]
    last_agent: str | None = None
    routing_log: list[dict] = Field(default_factory=list)
    context: dict = Field(default_factory=dict)
    created_at: str
    updated_at: str
