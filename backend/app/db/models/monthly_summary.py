"""MonthlySummary ORM model — pre-aggregated monthly expense data."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Index, Integer, Numeric, String, func, JSON, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class MonthlySummary(Base):
    __tablename__ = "monthly_summaries"
    __table_args__ = (
        Index("idx_monthly_year_month", "year", "month"),
        Index("idx_monthly_category", "category"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    categories_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    month: Mapped[int] = mapped_column(Integer, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    total_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    transaction_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    avg_transaction: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    max_transaction: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"<MonthlySummary {self.year}-{self.month:02d} {self.category}: ${self.total_amount}>"
