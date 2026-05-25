import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.database.models.user import User


class PerformanceData(Base):
    """ORM model — maps to `performance_data` table."""

    __tablename__ = "performance_data"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    subject: Mapped[str] = mapped_column(String(100), nullable=False)
    score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    study_hours: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), default=0)
    attendance_pct: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), default=0)
    predicted_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    risk_level: Mapped[str] = mapped_column(String(50), default="medium")
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="performance_data")
