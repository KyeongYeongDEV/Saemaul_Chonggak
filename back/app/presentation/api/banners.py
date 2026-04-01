from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.cache.cache_service import CacheService
from app.infrastructure.cache.redis_client import get_redis
from app.infrastructure.persistence.database import get_db
from app.infrastructure.persistence.product_repo import SQLBannerRepository
from app.presentation.schemas.common import ApiResponse
from app.presentation.schemas.product import BannerResponse

router = APIRouter(prefix="/banners", tags=["Banners"])


@router.get("", response_model=ApiResponse[list[BannerResponse]])
async def list_banners(db: AsyncSession = Depends(get_db), redis=Depends(get_redis)):
    cache = CacheService(redis)

    async def load():
        banners = await SQLBannerRepository(db).list_active()
        return [{"id": b.id, "title": b.title, "image_url": b.image_url, "link_url": b.link_url, "sort_order": b.sort_order} for b in banners]

    data = await cache.get_or_set("banner:list", 3600, load)
    return ApiResponse(data=data)
