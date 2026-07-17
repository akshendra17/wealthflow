"""Statement ORM model — represents an uploaded bank/CC statement."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func, JSON, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Statement(Base):
    __tablename__ = "statements"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    original_filename: Mapped[str] = mapped_column(String(500), nullable=False)
    file_type: Mapped[str] = mapped_column(
        String(10), nullable=False, default="CSV"
    )  # CSV, PDF
    bank_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    statement_month: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    statement_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    raw_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    total_transactions: Mapped[int] = mapped_column(Integer, default=0)
    total_debit: Mapped[float] = mapped_column(default=0.0)
    total_credit: Mapped[float] = mapped_column(default=0.0)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="statements")
    transactions: Mapped[List["Transaction"]] = relationship(
        "Transaction", back_populates="statement", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Statement {self.original_filename} ({self.id})>"
