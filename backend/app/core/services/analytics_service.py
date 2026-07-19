"""Analytics service — aggregation queries for dashboard data."""

from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.monthly_summary import MonthlySummary
from app.db.models.statement import Statement
from app.db.models.transaction import Transaction


class AnalyticsService:
    """Provides analytics and aggregation queries for the dashboard."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_monthly_summary(
        self, year: int, month: int, user_id: uuid.UUID, bank_name: Optional[str] = None
    ) -> dict:
        """Get the expense summary for a specific month, scoped to user (and optionally bank)."""
        if bank_name:
            result = await self.db.execute(
                select(
                    Transaction.category,
                    func.sum(Transaction.amount).label("total_amount"),
                    func.count(Transaction.id).label("transaction_count"),
                    func.avg(Transaction.amount).label("avg_transaction"),
                    func.max(Transaction.amount).label("max_transaction"),
                )
                .join(Statement, Transaction.statement_id == Statement.id)
                .where(
                    Statement.user_id == user_id,
                    Statement.bank_name == bank_name,
                    Statement.statement_year == year,
                    Statement.statement_month == month,
                    Transaction.transaction_type == "DEBIT",
                )
                .group_by(Transaction.category)
            )
            summaries = result.all()
            total_expenses = sum(float(s.total_amount or 0) for s in summaries)
            categories = [
                {
                    "category": s.category,
                    "total_amount": float(s.total_amount or 0),
                    "transaction_count": s.transaction_count,
                    "avg_transaction": float(s.avg_transaction or 0),
                    "max_transaction": float(s.max_transaction or 0),
                    "percentage": round(
                        (float(s.total_amount or 0) / total_expenses * 100)
                        if total_expenses > 0
                        else 0,
                        1,
                    ),
                }
                for s in summaries
            ]
            categories.sort(key=lambda x: x["total_amount"], reverse=True)
            return {
                "year": year,
                "month": month,
                "total_expenses": float(total_expenses),
                "category_count": len(categories),
                "categories": categories,
            }
        else:
            result = await self.db.execute(
                select(MonthlySummary)
                .where(
                    MonthlySummary.year == year,
                    MonthlySummary.month == month,
                    MonthlySummary.user_id == user_id,
                )
                .order_by(MonthlySummary.total_amount.desc())
            )
            summaries = result.scalars().all()

            total_expenses = sum(s.total_amount for s in summaries)
            categories = [
                {
                    "category": s.category,
                    "total_amount": float(s.total_amount),
                    "transaction_count": s.transaction_count,
                    "avg_transaction": float(s.avg_transaction),
                    "max_transaction": float(s.max_transaction),
                    "percentage": round(
                        (s.total_amount / total_expenses * 100)
                        if total_expenses > 0
                        else 0,
                        1,
                    ),
                }
                for s in summaries
            ]

            return {
                "year": year,
                "month": month,
                "total_expenses": float(total_expenses),
                "category_count": len(categories),
                "categories": categories,
            }

    async def get_category_breakdown(
        self, year: int, month: int, user_id: uuid.UUID, bank_name: Optional[str] = None
    ) -> list[dict]:
        """Get detailed category breakdown for a month with top transactions per category."""
        # We can reuse get_monthly_summary to get the base categories
        summary = await self.get_monthly_summary(year, month, user_id, bank_name)
        categories = summary["categories"]
        
        breakdown = []
        for cat in categories:
            # Get top 5 transactions for this category, scoped to user (and bank)
            query = (
                select(Transaction)
                .join(Statement, Transaction.statement_id == Statement.id)
                .where(
                    Statement.user_id == user_id,
                    Statement.statement_year == year,
                    Statement.statement_month == month,
                    Transaction.category == cat["category"],
                    Transaction.transaction_type == "DEBIT",
                )
                .order_by(Transaction.amount.desc())
                .limit(5)
            )
            
            if bank_name:
                query = query.where(Statement.bank_name == bank_name)
                
            txn_result = await self.db.execute(query)
            top_transactions = [
                {
                    "id": str(t.id),
                    "description": t.description,
                    "amount": float(t.amount),
                    "date": t.transaction_date.isoformat(),
                }
                for t in txn_result.scalars().all()
            ]

            breakdown.append(
                {
                    "category": cat["category"],
                    "total_amount": cat["total_amount"],
                    "transaction_count": cat["transaction_count"],
                    "percentage": cat["percentage"],
                    "avg_transaction": cat["avg_transaction"],
                    "max_transaction": cat["max_transaction"],
                    "top_transactions": top_transactions,
                }
            )

        return breakdown

    async def get_trends(
        self, num_months: int = 6, user_id: uuid.UUID = None, bank_name: Optional[str] = None
    ) -> dict:
        """Get multi-month expense trend data for chart visualization."""
        if bank_name:
            # Group directly from transactions
            result = await self.db.execute(
                select(
                    Statement.statement_year.label("year"),
                    Statement.statement_month.label("month"),
                    func.sum(Transaction.amount).label("total"),
                )
                .join(Statement, Transaction.statement_id == Statement.id)
                .where(
                    Statement.user_id == user_id,
                    Statement.bank_name == bank_name,
                    Transaction.transaction_type == "DEBIT"
                )
                .group_by(
                    Statement.statement_year,
                    Statement.statement_month
                )
                .order_by(
                    Statement.statement_year.desc(),
                    Statement.statement_month.desc()
                )
                .limit(num_months)
            )
            monthly_totals_raw = result.all()
            monthly_totals_raw = list(reversed(monthly_totals_raw))

            months = [
                {"year": int(r.year), "month": int(r.month), "label": f"{int(r.year)}-{int(r.month):02d}"}
                for r in monthly_totals_raw
            ]
            totals = [float(r.total) for r in monthly_totals_raw]

            # Get per-category trends for the selected months
            if monthly_totals_raw:
                oldest = monthly_totals_raw[0]
                
                cat_result = await self.db.execute(
                    select(
                        Transaction.category,
                        Statement.statement_year.label("year"),
                        Statement.statement_month.label("month"),
                        func.sum(Transaction.amount).label("total_amount"),
                    )
                    .join(Statement, Transaction.statement_id == Statement.id)
                    .where(
                        Statement.user_id == user_id,
                        Statement.bank_name == bank_name,
                        Transaction.transaction_type == "DEBIT",
                        (Statement.statement_year > oldest.year)
                        | (
                            (Statement.statement_year == oldest.year)
                            & (Statement.statement_month >= oldest.month)
                        ),
                    )
                    .group_by(
                        Transaction.category,
                        Statement.statement_year,
                        Statement.statement_month
                    )
                    .order_by("year", "month")
                )
                cat_rows = cat_result.all()
                
                category_trends: dict[str, list[float]] = {}
                for row in cat_rows:
                    if row.category not in category_trends:
                        category_trends[row.category] = [0.0] * len(months)
                    for i, m in enumerate(months):
                        if m["year"] == int(row.year) and m["month"] == int(row.month):
                            category_trends[row.category][i] = float(row.total_amount)
                            break
            else:
                category_trends = {}

        else:
            # Use MonthlySummary
            result = await self.db.execute(
                select(
                    MonthlySummary.year,
                    MonthlySummary.month,
                    func.sum(MonthlySummary.total_amount).label("total"),
                )
                .where(MonthlySummary.user_id == user_id)
                .group_by(MonthlySummary.year, MonthlySummary.month)
                .order_by(MonthlySummary.year.desc(), MonthlySummary.month.desc())
                .limit(num_months)
            )
            monthly_totals_raw = result.all()
            monthly_totals_raw = list(reversed(monthly_totals_raw))

            months = [
                {"year": r.year, "month": r.month, "label": f"{r.year}-{r.month:02d}"}
                for r in monthly_totals_raw
            ]
            totals = [float(r.total) for r in monthly_totals_raw]

            if monthly_totals_raw:
                oldest = monthly_totals_raw[0]

                cat_result = await self.db.execute(
                    select(
                        MonthlySummary.category,
                        MonthlySummary.year,
                        MonthlySummary.month,
                        MonthlySummary.total_amount,
                    )
                    .where(
                        MonthlySummary.user_id == user_id,
                        (MonthlySummary.year > oldest.year)
                        | (
                            (MonthlySummary.year == oldest.year)
                            & (MonthlySummary.month >= oldest.month)
                        ),
                    )
                    .order_by(MonthlySummary.year, MonthlySummary.month)
                )
                cat_rows = cat_result.all()

                category_trends: dict[str, list[float]] = {}
                for row in cat_rows:
                    if row.category not in category_trends:
                        category_trends[row.category] = [0.0] * len(months)
                    for i, m in enumerate(months):
                        if m["year"] == row.year and m["month"] == row.month:
                            category_trends[row.category][i] = float(row.total_amount)
                            break
            else:
                category_trends = {}

        # Calculate month-over-month change
        mom_change = None
        mom_change_pct = None
        if len(totals) >= 2:
            mom_change = totals[-1] - totals[-2]
            mom_change_pct = round(
                (mom_change / totals[-2] * 100) if totals[-2] > 0 else 0, 1
            )

        return {
            "months": months,
            "totals": totals,
            "category_trends": category_trends,
            "mom_change": mom_change,
            "mom_change_pct": mom_change_pct,
        }

    async def get_dashboard_summary(self, user_id: uuid.UUID, bank_name: Optional[str] = None) -> dict:
        """Get a high-level dashboard summary with the latest month's data."""
        if bank_name:
            # Find latest month from transactions
            result = await self.db.execute(
                select(
                    Statement.statement_year.label("year"), 
                    Statement.statement_month.label("month")
                )
                .join(Statement, Transaction.statement_id == Statement.id)
                .where(
                    Statement.user_id == user_id,
                    Statement.bank_name == bank_name
                )
                .group_by(
                    Statement.statement_year, 
                    Statement.statement_month
                )
                .order_by(
                    Statement.statement_year.desc(), 
                    Statement.statement_month.desc()
                )
                .limit(1)
            )
            latest = result.first()
            if latest:
                latest = type('obj', (object,), {'year': int(latest.year), 'month': int(latest.month)})
        else:
            result = await self.db.execute(
                select(MonthlySummary.year, MonthlySummary.month)
                .where(MonthlySummary.user_id == user_id)
                .group_by(MonthlySummary.year, MonthlySummary.month)
                .order_by(MonthlySummary.year.desc(), MonthlySummary.month.desc())
                .limit(1)
            )
            latest = result.first()

        if not latest:
            return {
                "has_data": False,
                "latest_month": None,
                "total_expenses": 0,
                "category_count": 0,
                "categories": [],
                "trends": None,
            }

        summary = await self.get_monthly_summary(latest.year, latest.month, user_id, bank_name)
        trends = await self.get_trends(6, user_id, bank_name)

        return {
            "has_data": True,
            "latest_month": {"year": latest.year, "month": latest.month},
            **summary,
            "trends": trends,
        }
