"""Category API endpoints — list and create categories."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.services.categorizer import get_default_categories
from app.db.models.category import Category
from app.db.models.user import User
from app.db.session import get_db
from app.dependencies import get_current_user
from app.schemas.category import CategoryCreate, CategoryRead

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=list[CategoryRead])
async def list_categories(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all expense categories (system defaults + user specific)."""
    query = select(Category).where(
        or_(Category.user_id == current_user.id, Category.user_id.is_(None))
    ).order_by(Category.display_order, Category.name)
    
    result = await db.execute(query)
    categories = list(result.scalars().all())

    # If no categories exist yet, return defaults from the categorizer
    if not categories:
        defaults = get_default_categories()
        for order, (name, data) in enumerate(defaults.items()):
            cat = Category(
                name=name,
                icon=data.get("icon", "📦"),
                color_hex=data.get("color", "#859399"),
                display_order=order,
            )
            db.add(cat)

        await db.flush()
        await db.commit()
        
        result = await db.execute(query)
        categories = list(result.scalars().all())

    return categories


@router.post("/", response_model=CategoryRead, status_code=201)
async def create_category(
    data: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new expense category."""
    # Get the next display order
    result = await db.execute(
        select(Category.display_order)
        .where(or_(Category.user_id == current_user.id, Category.user_id.is_(None)))
        .order_by(Category.display_order.desc())
        .limit(1)
    )
    max_order = result.scalar() or 0

    category = Category(
        user_id=current_user.id,
        name=data.name,
        icon=data.icon,
        color_hex=data.color_hex,
        display_order=max_order + 1,
    )
    db.add(category)
    await db.flush()
    await db.commit()
    await db.refresh(category)
    return category
