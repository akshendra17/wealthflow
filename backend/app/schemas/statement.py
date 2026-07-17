"""Pydantic schemas for statement endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class StatementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    original_filename: str
    file_type: str
    bank_name: Optional[str] = None
    statement_month: Optional[int] = None
    statement_year: Optional[int] = None
    total_transactions: int
    total_debit: float
    total_credit: float
    notes: Optional[str] = None
    uploaded_at: datetime
    created_at: datetime


class StatementDetailRead(StatementRead):
    """Statement with its transactions."""
    transactions: List["TransactionRead"] = []


# Avoid circular import
from app.schemas.transaction import TransactionRead  # noqa: E402

StatementDetailRead.model_rebuild()
