"""Pydantic schemas for category endpoints."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    icon: str
    color_hex: str
    display_order: int


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    icon: str = Field(default="📦", max_length=50)
    color_hex: str = Field(default="#859399", pattern=r"^#[0-9a-fA-F]{6}$")
