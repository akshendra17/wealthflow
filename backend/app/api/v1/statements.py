"""Statement API endpoints — upload, list, get, delete."""

from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.services.statement_service import StatementService
from app.db.models.user import User
from app.db.session import get_db
from app.dependencies import get_current_user
from app.schemas.statement import StatementDetailRead, StatementRead

router = APIRouter(prefix="/statements", tags=["statements"])


@router.post("/upload", response_model=StatementRead, status_code=201)
async def upload_statement(
    file: UploadFile = File(...),
    bank_name: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload a bank/CC statement (CSV or PDF) and parse transactions."""
    content = await file.read()
    service = StatementService(db)
    statement = await service.upload_and_parse(
        filename=file.filename or "unknown.csv",
        file_content=content,
        user_id=current_user.id,
        bank_name=bank_name,
    )
    return statement


@router.get("/", response_model=list[StatementRead])
async def list_statements(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all uploaded statements for the current user."""
    service = StatementService(db)
    return await service.list_statements(user_id=current_user.id)


@router.get("/{statement_id}", response_model=StatementDetailRead)
async def get_statement(
    statement_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single statement with its transactions."""
    service = StatementService(db)
    statement = await service.get_statement(statement_id, user_id=current_user.id)
    # Eagerly load transactions
    await db.refresh(statement, ["transactions"])
    return statement


@router.delete("/all", status_code=204)
async def delete_all_statements(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete all statements and transactions for the current user."""
    service = StatementService(db)
    await service.delete_all_statements(user_id=current_user.id)


@router.delete("/{statement_id}", status_code=204)
async def delete_statement(
    statement_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a statement and all its transactions."""
    service = StatementService(db)
    await service.delete_statement(statement_id, user_id=current_user.id)
