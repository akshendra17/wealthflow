"""Transaction API endpoints — list, filter, re-categorize."""

from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.db.models.statement import Statement
from app.db.models.transaction import Transaction
from app.db.models.user import User
from app.db.session import get_db
from app.dependencies import get_current_user
from app.schemas.transaction import (
    TransactionCategorize,
    TransactionListResponse,
    TransactionRead,
)

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("/", response_model=TransactionListResponse)
async def list_transactions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None),
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2000, le=2100),
    transaction_type: Optional[str] = Query(None, pattern="^(DEBIT|CREDIT)$"),
    search: Optional[str] = Query(None, max_length=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List transactions with filtering and pagination, scoped to current user."""
    # Base queries join through Statement to filter by user_id
    query = (
        select(Transaction)
        .join(Statement, Transaction.statement_id == Statement.id)
        .where(Statement.user_id == current_user.id)
    )
    count_query = (
        select(func.count())
        .select_from(Transaction)
        .join(Statement, Transaction.statement_id == Statement.id)
        .where(Statement.user_id == current_user.id)
    )

    # Apply filters
    if category:
        query = query.where(Transaction.category == category)
        count_query = count_query.where(Transaction.category == category)
    if month:
        query = query.where(extract("month", Transaction.transaction_date) == month)
        count_query = count_query.where(extract("month", Transaction.transaction_date) == month)
    if year:
        query = query.where(extract("year", Transaction.transaction_date) == year)
        count_query = count_query.where(extract("year", Transaction.transaction_date) == year)
    if transaction_type:
        query = query.where(Transaction.transaction_type == transaction_type)
        count_query = count_query.where(Transaction.transaction_type == transaction_type)
    if search:
        search_filter = Transaction.description.ilike(f"%{search}%")
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)

    # Get total count
    total = (await db.execute(count_query)).scalar() or 0

    # Apply pagination and sorting
    result = await db.execute(
        query.order_by(Transaction.transaction_date.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    transactions = list(result.scalars().all())

    return TransactionListResponse(
        items=transactions,
        total=total,
        page=page,
        page_size=page_size,
        has_next=(page * page_size) < total,
        has_previous=page > 1,
    )


@router.patch("/{transaction_id}/categorize", response_model=TransactionRead)
async def categorize_transaction(
    transaction_id: uuid.UUID,
    data: TransactionCategorize,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Re-categorize a transaction manually. Scoped to current user."""
    result = await db.execute(
        select(Transaction)
        .join(Statement, Transaction.statement_id == Statement.id)
        .where(
            Transaction.id == transaction_id,
            Statement.user_id == current_user.id,
        )
    )
    transaction = result.scalar_one_or_none()
    if not transaction:
        raise NotFoundError("Transaction", str(transaction_id))

    transaction.category = data.category
    transaction.subcategory = data.subcategory
    transaction.is_manually_categorized = True

    await db.flush()
    await db.commit()
    await db.refresh(transaction)
    return transaction
