from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.admin.get_stats import GetStatsUseCase
from app.core.dependencies import require_admin
from app.infrastructure.persistence.database import get_db
from app.presentation.schemas.common import ApiResponse

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/stats", response_model=ApiResponse[dict])
async def get_stats(
    days: int = Query(7, ge=1, le=90),
    admin: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await GetStatsUseCase(db).execute(days)
    return ApiResponse(data={
        "daily_sales": result.daily_sales,
        "total_revenue": result.total_revenue,
        "total_orders": result.total_orders,
    })
