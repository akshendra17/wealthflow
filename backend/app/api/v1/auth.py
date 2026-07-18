"""Auth API endpoints — register, login, refresh, me."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from app.dependencies import get_current_user
from app.config import settings

from app.core.services.auth_service import (
    authenticate_user,
    create_token_pair,
    register_user,
    verify_token,
    AuthError,
)
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserRead,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def _set_refresh_cookie(response: Response, refresh_token: str):
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False if settings.environment == "development" else True,
        samesite="lax",
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
    )


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(
    request: Request,
    body: RegisterRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """Create a new user account and return access token (refresh in cookie)."""
    user = await register_user(db, body.email, body.name, body.password)
    tokens = create_token_pair(user)
    
    _set_refresh_cookie(response, tokens["refresh_token"])
    
    return TokenResponse(
        access_token=tokens["access_token"], 
        user=UserRead.model_validate(user)
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    body: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """Authenticate with email and password. Returns access token (refresh in cookie)."""
    user = await authenticate_user(db, body.email, body.password)
    tokens = create_token_pair(user)
    
    _set_refresh_cookie(response, tokens["refresh_token"])
    
    return TokenResponse(
        access_token=tokens["access_token"], 
        user=UserRead.model_validate(user)
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """Exchange a refresh cookie for a new access token + refresh cookie pair."""
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise AuthError("Refresh token missing.")

    payload = verify_token(refresh_token, expected_type="refresh")
    user_id = payload.get("sub")

    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    user = result.scalar_one_or_none()
    if not user:
        raise AuthError("User not found.")

    tokens = create_token_pair(user)
    
    _set_refresh_cookie(response, tokens["refresh_token"])
    
    return TokenResponse(
        access_token=tokens["access_token"], 
        user=UserRead.model_validate(user)
    )


@router.post("/logout")
async def logout(response: Response):
    """Clear the refresh token cookie."""
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=False if settings.environment == "development" else True,
        samesite="lax"
    )
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserRead)
async def get_me(
    current_user: User = Depends(get_current_user),
):
    """Get the currently authenticated user's profile."""
    return current_user
