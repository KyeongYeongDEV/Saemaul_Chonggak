from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.product.get_product import GetProductUseCase
from app.application.product.list_products import ListProductsCommand, ListProductsUseCase
from app.application.product.list_time_sale import ListTimeSaleUseCase
from app.application.product.search_products import SearchProductsUseCase
from app.infrastructure.cache.cache_service import CacheService
from app.infrastructure.cache.redis_client import get_redis
from app.infrastructure.persistence.database import get_db
from app.infrastructure.persistence.product_repo import SQLProductRepository
from app.presentation.schemas.common import ApiResponse, PaginatedData
from app.presentation.schemas.product import ProductDetail, ProductSummary

router = APIRouter(prefix="/products", tags=["Products"])


def _cache(redis=Depends(get_redis)) -> CacheService:
    return CacheService(redis)


@router.get("", response_model=ApiResponse[PaginatedData[dict]])
async def list_products(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    category_id: int | None = None,
    sort: str = Query("latest", pattern="^(latest|price_asc|price_desc)$"),
    db: AsyncSession = Depends(get_db),
    cache: CacheService = Depends(_cache),
):
    result = await ListProductsUseCase(SQLProductRepository(db), cache).execute(
        ListProductsCommand(page=page, size=size, category_id=category_id, sort=sort)
    )
    return ApiResponse(data=PaginatedData(items=result.items, total=result.total, page=page, size=size))


@router.get("/search", response_model=ApiResponse[PaginatedData[dict]])
async def search_products(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    result = await SearchProductsUseCase(SQLProductRepository(db)).execute(q, page, size)
    items = [{"id": p.id, "name": p.name, "price": p.price, "thumbnail_url": p.thumbnail_url} for p in result.items]
    return ApiResponse(data=PaginatedData(items=items, total=result.total, page=page, size=size))


@router.get("/time-sale", response_model=ApiResponse[list[dict]])
async def list_time_sale(db: AsyncSession = Depends(get_db)):
    products = await ListTimeSaleUseCase(SQLProductRepository(db)).execute()
    items = [
        {"id": p.id, "name": p.name, "price": p.price, "time_sale_price": p.time_sale_price,
         "time_sale_end": str(p.time_sale_end), "thumbnail_url": p.thumbnail_url, "stock": p.stock}
        for p in products
    ]
    return ApiResponse(data=items)


@router.get("/{product_id}", response_model=ApiResponse[dict])
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    cache: CacheService = Depends(_cache),
):
    data = await GetProductUseCase(SQLProductRepository(db), cache).execute(product_id)
    return ApiResponse(data=data)
