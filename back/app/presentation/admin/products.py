from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.admin.manage_products import AdminProductUseCase, CreateProductCommand, UpdateProductCommand
from app.core.dependencies import require_admin
from app.infrastructure.cache.cache_service import CacheService
from app.infrastructure.cache.redis_client import get_redis
from app.infrastructure.persistence.audit_log_repo import AuditLogRepository
from app.infrastructure.persistence.database import get_db
from app.infrastructure.persistence.product_repo import SQLProductRepository
from app.presentation.schemas.common import ApiResponse, PaginatedData
from pydantic import BaseModel

router = APIRouter(prefix="/admin/products", tags=["Admin"])


class ProductCreateRequest(BaseModel):
    category_id: int
    name: str
    description: str | None = None
    price: int
    sale_price: int | None = None
    stock: int
    thumbnail_url: str | None = None


class ProductUpdateRequest(ProductCreateRequest):
    is_active: bool = True


@router.get("", response_model=ApiResponse[PaginatedData[dict]])
async def list_products(
    page: int = Query(1, ge=1), size: int = Query(20),
    admin: dict = Depends(require_admin), db: AsyncSession = Depends(get_db),
):
    items, total = await SQLProductRepository(db).list(page, size, None, "latest")
    data = [{"id": p.id, "name": p.name, "price": p.price, "stock": p.stock, "is_active": p.is_active} for p in items]
    return ApiResponse(data=PaginatedData(items=data, total=total, page=page, size=size))


@router.post("", response_model=ApiResponse[dict], status_code=201)
async def create_product(
    body: ProductCreateRequest, request: Request,
    admin: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db), redis=Depends(get_redis),
):
    use_case = AdminProductUseCase(SQLProductRepository(db), AuditLogRepository(db), CacheService(redis))
    product = await use_case.create(CreateProductCommand(
        category_id=body.category_id, name=body.name, description=body.description,
        price=body.price, sale_price=body.sale_price, stock=body.stock,
        thumbnail_url=body.thumbnail_url, admin_id=int(admin["sub"]),
        ip_address=request.client.host if request.client else None,
    ))
    return ApiResponse(data={"id": product.id, "name": product.name})


@router.put("/{product_id}", status_code=204)
async def update_product(
    product_id: int, body: ProductUpdateRequest, request: Request,
    admin: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db), redis=Depends(get_redis),
):
    use_case = AdminProductUseCase(SQLProductRepository(db), AuditLogRepository(db), CacheService(redis))
    await use_case.update(UpdateProductCommand(
        product_id=product_id, category_id=body.category_id, name=body.name,
        description=body.description, price=body.price, sale_price=body.sale_price,
        stock=body.stock, thumbnail_url=body.thumbnail_url, is_active=body.is_active,
        admin_id=int(admin["sub"]), ip_address=request.client.host if request.client else None,
    ))


@router.delete("/{product_id}", status_code=204)
async def delete_product(
    product_id: int, request: Request,
    admin: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db), redis=Depends(get_redis),
):
    use_case = AdminProductUseCase(SQLProductRepository(db), AuditLogRepository(db), CacheService(redis))
    await use_case.delete(product_id, int(admin["sub"]), request.client.host if request.client else None)
