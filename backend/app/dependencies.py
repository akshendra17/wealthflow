"""FastAPI dependency injection helpers."""

from __future__ import annotations

import uuid

from fastapi import Depends, Header
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.services.auth_service import AuthError, verify_token
from app.db.models.user import User
from app.db.session import get_db


async def get_current_user(
    authorization: str = Header(..., description="Bearer <access_token>"),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Extract and validate the JWT access token from the Authorization header.

    Returns the authenticated User ORM instance.
    Raises 401 if the token is missing, invalid, or expired.
    """
    if not authorization.startswith("Bearer "):
        raise AuthError("Authorization header must start with 'Bearer '.")

    token = authorization[7:]  # Strip "Bearer "
    payload = verify_token(token, expected_type="access")

    user_id = payload.get("sub")
    if not user_id:
        raise AuthError("Token payload missing 'sub' claim.")

    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    user = result.scalar_one_or_none()

    if not user:
        raise AuthError("User not found.")

    return user
