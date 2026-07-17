"""Transaction ORM model — individual parsed transaction from a statement."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    func,
    JSON,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = (
        Index("idx_transactions_date", "transaction_date"),
        Index("idx_transactions_category", "category"),
        Index("idx_transactions_statement", "statement_id"),
        Index("idx_transactions_type", "transaction_type"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    statement_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("statements.id", ondelete="CASCADE"), nullable=False
    )

    transaction_date: Mapped[date] = mapped_column(Date, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    transaction_type: Mapped[str] = mapped_column(
        String(10), nullable=False, default="DEBIT"
    )  # DEBIT, CREDIT

    category: Mapped[str] = mapped_column(String(100), nullable=False, default="Misc")
    subcategory: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    original_category: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    is_manually_categorized: Mapped[bool] = mapped_column(Boolean, default=False)

    raw_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    statement: Mapped["Statement"] = relationship("Statement", back_populates="transactions")

    def __repr__(self) -> str:
        return f"<Transaction {self.description[:30]} ${self.amount} ({self.category})>"
