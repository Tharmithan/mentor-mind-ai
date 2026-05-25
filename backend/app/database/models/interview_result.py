import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.database.models.user import User


class InterviewResult(Base):
    """ORM model — maps to `interview_results` table."""

    __tablename__ = "interview_results"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    mode: Mapped[str] = mapped_column(String(50), default="general")
    overall_score: Mapped[Decimal | None] = mapped_column(Numeric(3, 2))
    communication_score: Mapped[Decimal | None] = mapped_column(Numeric(3, 2))
    technical_score: Mapped[Decimal | None] = mapped_column(Numeric(3, 2))
    confidence_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    feedback_summary: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="interview_results")
