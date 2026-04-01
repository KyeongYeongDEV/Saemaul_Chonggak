from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.admin.get_dashboard import GetDashboardUseCase
from app.core.dependencies import require_admin
from app.infrastructure.cache.cache_service import CacheService
from app.infrastructure.cache.redis_client import get_redis
from app.infrastructure.persistence.database import get_db
from app.presentation.schemas.common import ApiResponse

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/dashboard", response_model=ApiResponse[dict])
async def get_dashboard(
    _: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    result = await GetDashboardUseCase(db, CacheService(redis)).execute()
    return ApiResponse(data={
        "mau": result.mau, "total_sales_today": result.total_sales_today,
        "total_orders_today": result.total_orders_today, "pending_orders": result.pending_orders,
    })
