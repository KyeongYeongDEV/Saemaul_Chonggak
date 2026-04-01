from datetime import datetime

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.admin.manage_banners import AdminBannerUseCase, BannerCommand
from app.core.dependencies import require_admin
from app.infrastructure.cache.cache_service import CacheService
from app.infrastructure.cache.redis_client import get_redis
from app.infrastructure.persistence.audit_log_repo import AuditLogRepository
from app.infrastructure.persistence.database import get_db
from app.infrastructure.persistence.product_repo import SQLBannerRepository
from app.presentation.schemas.common import ApiResponse
from pydantic import BaseModel

router = APIRouter(prefix="/admin/banners", tags=["Admin"])


class BannerRequest(BaseModel):
    title: str
    image_url: str
    link_url: str | None = None
    sort_order: int = 0
    is_active: bool = True
    started_at: datetime | None = None
    ended_at: datetime | None = None


@router.get("", response_model=ApiResponse[list[dict]])
async def list_banners(admin: dict = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    banners = await SQLBannerRepository(db).list_active()
    return ApiResponse(data=[{"id": b.id, "title": b.title, "image_url": b.image_url, "is_active": b.is_active} for b in banners])


@router.post("", status_code=201)
async def create_banner(
    body: BannerRequest, request: Request,
    admin: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db), redis=Depends(get_redis),
):
    use_case = AdminBannerUseCase(SQLBannerRepository(db), AuditLogRepository(db), CacheService(redis))
    banner = await use_case.create(BannerCommand(
        title=body.title, image_url=body.image_url, link_url=body.link_url,
        sort_order=body.sort_order, is_active=body.is_active,
        started_at=body.started_at, ended_at=body.ended_at,
        admin_id=int(admin["sub"]), ip_address=request.client.host if request.client else None,
    ))
    return ApiResponse(data={"id": banner.id})


@router.put("/{banner_id}", status_code=204)
async def update_banner(
    banner_id: int, body: BannerRequest, request: Request,
    admin: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db), redis=Depends(get_redis),
):
    use_case = AdminBannerUseCase(SQLBannerRepository(db), AuditLogRepository(db), CacheService(redis))
    await use_case.update(banner_id, BannerCommand(
        title=body.title, image_url=body.image_url, link_url=body.link_url,
        sort_order=body.sort_order, is_active=body.is_active,
        started_at=body.started_at, ended_at=body.ended_at,
        admin_id=int(admin["sub"]), ip_address=request.client.host if request.client else None,
    ))


@router.delete("/{banner_id}", status_code=204)
async def delete_banner(
    banner_id: int, request: Request,
    admin: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db), redis=Depends(get_redis),
):
    use_case = AdminBannerUseCase(SQLBannerRepository(db), AuditLogRepository(db), CacheService(redis))
    await use_case.delete(banner_id, int(admin["sub"]), request.client.host if request.client else None)
