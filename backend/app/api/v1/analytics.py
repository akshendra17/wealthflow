"""Analytics API endpoints — monthly summaries, trends, dashboard."""

from __future__ import annotations

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.services.analytics_service import AnalyticsService
from app.db.models.user import User
from app.db.session import get_db
from app.dependencies import get_current_user

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/dashboard")
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    bank_name: Optional[str] = Query(None),
):
    """Get the main dashboard summary with latest month data and trends."""
    service = AnalyticsService(db)
    return await service.get_dashboard_summary(user_id=current_user.id, bank_name=bank_name)


@router.get("/monthly-summary")
async def get_monthly_summary(
    year: int = Query(..., ge=2000, le=2100),
    month: int = Query(..., ge=1, le=12),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    bank_name: Optional[str] = Query(None),
):
    """Get expense summary for a specific month."""
    service = AnalyticsService(db)
    return await service.get_monthly_summary(year, month, user_id=current_user.id, bank_name=bank_name)


@router.get("/category-breakdown")
async def get_category_breakdown(
    year: int = Query(..., ge=2000, le=2100),
    month: int = Query(..., ge=1, le=12),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    bank_name: Optional[str] = Query(None),
):
    """Get detailed category breakdown for a month."""
    service = AnalyticsService(db)
    return await service.get_category_breakdown(year, month, user_id=current_user.id, bank_name=bank_name)


@router.get("/trends")
async def get_trends(
    months: int = Query(6, ge=2, le=24),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    bank_name: Optional[str] = Query(None),
):
    """Get multi-month expense trends for chart visualization."""
    service = AnalyticsService(db)
    return await service.get_trends(months, user_id=current_user.id, bank_name=bank_name)
