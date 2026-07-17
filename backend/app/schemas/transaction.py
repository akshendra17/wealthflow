"""Pydantic schemas for transaction endpoints."""

from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TransactionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    statement_id: UUID
    transaction_date: date
    description: str
    amount: float
    transaction_type: str
    category: str
    subcategory: Optional[str] = None
    is_manually_categorized: bool
    created_at: datetime


class TransactionCategorize(BaseModel):
    """Request to re-categorize a transaction."""
    category: str = Field(..., min_length=1, max_length=100)
    subcategory: Optional[str] = None


class TransactionListResponse(BaseModel):
    items: List[TransactionRead]
    total: int
    page: int
    page_size: int
    has_next: bool
    has_previous: bool
