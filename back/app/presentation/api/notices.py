from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.cs.list_notices import ListNoticesUseCase
from app.infrastructure.persistence.cs_repo import SQLNoticeRepository
from app.infrastructure.persistence.database import get_db
from app.presentation.schemas.common import ApiResponse, PaginatedData

router = APIRouter(prefix="/notices", tags=["CS"])


@router.get("", response_model=ApiResponse[PaginatedData[dict]])
async def list_notices(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    result = await ListNoticesUseCase(SQLNoticeRepository(db)).execute(page, size)
    items = [
        {
            "id": n.id,
            "title": n.title,
            "content": n.content,
            "is_pinned": n.is_pinned,
            "created_at": n.created_at,
        }
        for n in result.items
    ]
    return ApiResponse(data=PaginatedData(items=items, total=result.total, page=page, size=size))
