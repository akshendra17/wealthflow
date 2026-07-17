"""Pydantic schemas for analytics endpoints."""

from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel


class CategorySummary(BaseModel):
    category: str
    total_amount: float
    transaction_count: int
    avg_transaction: float
    max_transaction: float
    percentage: float


class MonthlySummaryResponse(BaseModel):
    year: int
    month: int
    total_expenses: float
    category_count: int
    categories: List[CategorySummary]


class MonthLabel(BaseModel):
    year: int
    month: int
    label: str


class TrendsResponse(BaseModel):
    months: List[MonthLabel]
    totals: List[float]
    category_trends: Dict[str, List[float]]
    mom_change: Optional[float] = None
    mom_change_pct: Optional[float] = None


class DashboardResponse(BaseModel):
    has_data: bool
    latest_month: Optional[MonthLabel] = None
    total_expenses: float = 0
    category_count: int = 0
    categories: List[CategorySummary] = []
    trends: Optional[TrendsResponse] = None
