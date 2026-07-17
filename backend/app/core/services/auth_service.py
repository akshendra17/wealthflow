"""Authentication service — JWT tokens, password hashing, user registration/login."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from typing import Optional

import structlog
from jose import JWTError, jwt
import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.exceptions import AppError
from app.db.models.user import User

logger = structlog.get_logger()

# Password hashing context


class AuthError(AppError):
    """Authentication-related errors."""

    def __init__(self, message: str):
        super().__init__(message, code="UNAUTHORIZED")


class RegistrationError(AppError):
    """Registration-related errors."""

    def __init__(self, message: str):
        super().__init__(message, code="VALIDATION_ERROR")


# ── Password Utilities ──


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


# ── JWT Token Utilities ──


def create_access_token(user_id: uuid.UUID, email: str) -> str:
    """Create a short-lived access token (1 hour)."""
    payload = {
        "sub": str(user_id),
        "email": email,
        "type": "access",
        "exp": datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(user_id: uuid.UUID) -> str:
    """Create a long-lived refresh token (7 days)."""
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "exp": datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def verify_token(token: str, expected_type: str = "access") -> dict:
    """Decode and validate a JWT token. Returns the payload dict."""
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError as e:
        raise AuthError(f"Invalid or expired token: {str(e)}")

    token_type = payload.get("type")
    if token_type != expected_type:
        raise AuthError(f"Expected '{expected_type}' token, got '{token_type}'")

    return payload


# ── User Operations ──


async def register_user(
    db: AsyncSession,
    email: str,
    name: str,
    password: str,
) -> User:
    """Register a new user. Raises RegistrationError if email is taken."""
    # Check for existing user
    result = await db.execute(select(User).where(User.email == email))
    existing = result.scalar_one_or_none()
    if existing:
        raise RegistrationError(f"An account with email '{email}' already exists.")

    user = User(
        email=email.lower().strip(),
        name=name.strip(),
        password_hash=hash_password(password),
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    logger.info("user_registered", user_id=str(user.id), email=user.email)
    return user


async def authenticate_user(
    db: AsyncSession,
    email: str,
    password: str,
) -> User:
    """Authenticate a user by email and password. Raises AuthError on failure."""
    result = await db.execute(select(User).where(User.email == email.lower().strip()))
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.password_hash):
        raise AuthError("Invalid email or password.")

    logger.info("user_authenticated", user_id=str(user.id))
    return user


def create_token_pair(user: User) -> dict:
    """Create both access and refresh tokens for a user."""
    return {
        "access_token": create_access_token(user.id, user.email),
        "refresh_token": create_refresh_token(user.id),
        "token_type": "bearer",
    }
