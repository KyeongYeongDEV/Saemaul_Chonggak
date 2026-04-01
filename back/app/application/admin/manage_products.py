from dataclasses import dataclass
from datetime import datetime

from app.core.exceptions import ProductNotFoundError
from app.domain.product.entities import Product
from app.domain.product.repository import ProductRepository
from app.infrastructure.cache.cache_service import CacheService
from app.infrastructure.persistence.audit_log_repo import AuditLogRepository


@dataclass
class CreateProductCommand:
    category_id: int
    name: str
    description: str | None
    price: int
    sale_price: int | None
    stock: int
    thumbnail_url: str | None
    admin_id: int
    ip_address: str | None


@dataclass
class UpdateProductCommand:
    product_id: int
    category_id: int
    name: str
    description: str | None
    price: int
    sale_price: int | None
    stock: int
    thumbnail_url: str | None
    is_active: bool
    admin_id: int
    ip_address: str | None


class AdminProductUseCase:
    def __init__(
        self,
        product_repo: ProductRepository,
        audit_repo: AuditLogRepository,
        cache: CacheService,
    ):
        self._repo = product_repo
        self._audit = audit_repo
        self._cache = cache

    async def create(self, cmd: CreateProductCommand) -> Product:
        product = Product(
            id=None, category_id=cmd.category_id, name=cmd.name, description=cmd.description,
            price=cmd.price, sale_price=cmd.sale_price, stock=cmd.stock,
            thumbnail_url=cmd.thumbnail_url, is_active=True,
            is_time_sale=False, time_sale_start=None, time_sale_end=None,
            time_sale_price=None, time_sale_stock=None, created_at=datetime.utcnow(),
        )
        saved = await self._repo.save(product)
        await self._audit.write(
            admin_id=cmd.admin_id, action="CREATE_PRODUCT",
            target_type="product", target_id=saved.id, ip_address=cmd.ip_address,
        )
        await self._cache.invalidate_pattern("product:list:*")
        return saved

    async def update(self, cmd: UpdateProductCommand) -> Product:
        product = await self._repo.get_by_id(cmd.product_id)
        if not product:
            raise ProductNotFoundError()
        before = {"name": product.name, "price": product.price, "stock": product.stock}
        product.category_id = cmd.category_id
        product.name = cmd.name
        product.description = cmd.description
        product.price = cmd.price
        product.sale_price = cmd.sale_price
        product.stock = cmd.stock
        product.thumbnail_url = cmd.thumbnail_url
        product.is_active = cmd.is_active
        updated = await self._repo.update(product)
        await self._audit.write(
            admin_id=cmd.admin_id, action="UPDATE_PRODUCT",
            target_type="product", target_id=cmd.product_id,
            before_data=before, after_data={"name": cmd.name, "price": cmd.price},
            ip_address=cmd.ip_address,
        )
        await self._cache.invalidate(f"product:detail:{cmd.product_id}")
        await self._cache.invalidate_pattern("product:list:*")
        return updated

    async def delete(self, product_id: int, admin_id: int, ip_address: str | None) -> None:
        await self._repo.delete(product_id)
        await self._audit.write(
            admin_id=admin_id, action="DELETE_PRODUCT",
            target_type="product", target_id=product_id, ip_address=ip_address,
        )
        await self._cache.invalidate(f"product:detail:{product_id}")
        await self._cache.invalidate_pattern("product:list:*")
