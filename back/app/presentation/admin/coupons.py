from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.admin.manage_coupons import AdminCouponUseCase, CreateCouponCommand
from app.core.dependencies import require_admin
from app.infrastructure.cache.cache_service import CacheService
from app.infrastructure.cache.redis_client import get_redis
from app.infrastructure.persistence.audit_log_repo import AuditLogRepository
from app.infrastructure.persistence.coupon_repo import SQLCouponRepository
from app.infrastructure.persistence.database import get_db
from app.presentation.schemas.common import ApiResponse, PaginatedData
from pydantic import BaseModel

router = APIRouter(prefix="/admin/coupons", tags=["Admin"])


class CouponCreateRequest(BaseModel):
    code: str
    name: str
    type: str  # fixed | percent
    discount_value: int
    min_order_amount: int = 0
    max_discount: int | None = None
    total_stock: int
    started_at: datetime
    expired_at: datetime


@router.get("", response_model=ApiResponse[PaginatedData[dict]])
async def list_coupons(
    page: int = Query(1, ge=1), size: int = Query(20),
    admin: dict = Depends(require_admin), db: AsyncSession = Depends(get_db), redis=Depends(get_redis),
):
    use_case = AdminCouponUseCase(SQLCouponRepository(db), AuditLogRepository(db), CacheService(redis))
    coupons, total = await use_case.list(page, size)
    data = [{"id": c.id, "code": c.code, "name": c.name, "type": c.type.value, "issued_count": c.issued_count, "total_stock": c.total_stock} for c in coupons]
    return ApiResponse(data=PaginatedData(items=data, total=total, page=page, size=size))


@router.post("", status_code=201)
async def create_coupon(
    body: CouponCreateRequest, request: Request,
    admin: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db), redis=Depends(get_redis),
):
    use_case = AdminCouponUseCase(SQLCouponRepository(db), AuditLogRepository(db), CacheService(redis))
    coupon = await use_case.create(CreateCouponCommand(
        code=body.code, name=body.name, type=body.type,
        discount_value=body.discount_value, min_order_amount=body.min_order_amount,
        max_discount=body.max_discount, total_stock=body.total_stock,
        started_at=body.started_at, expired_at=body.expired_at,
        admin_id=int(admin["sub"]), ip_address=request.client.host if request.client else None,
    ))
    return ApiResponse(data={"id": coupon.id, "code": coupon.code})


@router.delete("/{coupon_id}", status_code=204)
async def delete_coupon(
    coupon_id: int, request: Request,
    admin: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db), redis=Depends(get_redis),
):
    use_case = AdminCouponUseCase(SQLCouponRepository(db), AuditLogRepository(db), CacheService(redis))
    await use_case.delete(coupon_id, int(admin["sub"]), request.client.host if request.client else None)
