from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.persistence.database import get_db
from app.infrastructure.persistence.product_repo import SQLCategoryRepository
from app.presentation.schemas.common import ApiResponse
from app.presentation.schemas.product import CategoryResponse

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=ApiResponse[list[CategoryResponse]])
async def list_categories(db: AsyncSession = Depends(get_db)):
    categories = await SQLCategoryRepository(db).list_active()
    return ApiResponse(data=[
        CategoryResponse(id=c.id, parent_id=c.parent_id, name=c.name, sort_order=c.sort_order)
        for c in categories
    ])
