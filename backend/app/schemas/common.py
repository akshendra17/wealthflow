"""Common Pydantic schemas shared across the API."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel


class ErrorDetail(BaseModel):
    field: Optional[str] = None
    message: str


class ErrorResponse(BaseModel):
    code: str
    message: str
    details: Optional[List[ErrorDetail]] = None


class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str = "0.1.0"
