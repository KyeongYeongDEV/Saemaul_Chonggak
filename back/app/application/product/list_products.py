from dataclasses import dataclass

from app.domain.product.entities import Product
from app.domain.product.repository import ProductRepository
from app.infrastructure.cache.cache_service import CacheService


@dataclass
class ListProductsCommand:
    page: int
    size: int
    category_id: int | None
    sort: str  # latest | price_asc | price_desc


@dataclass
class ListProductsResult:
    items: list[Product]
    total: int
    page: int
    size: int


class ListProductsUseCase:
    def __init__(self, product_repo: ProductRepository, cache: CacheService):
        self._repo = product_repo
        self._cache = cache

    async def execute(self, cmd: ListProductsCommand) -> ListProductsResult:
        cache_key = f"product:list:{cmd.category_id}:{cmd.page}:{cmd.size}:{cmd.sort}"

        async def load():
            items, total = await self._repo.list(cmd.page, cmd.size, cmd.category_id, cmd.sort)
            return {"items": [_product_to_dict(p) for p in items], "total": total}

        data = await self._cache.get_or_set(cache_key, 300, load)
        return ListProductsResult(
            items=data["items"], total=data["total"], page=cmd.page, size=cmd.size
        )


def _product_to_dict(p) -> dict:
    return {
        "id": p.id, "name": p.name, "price": p.price, "sale_price": p.sale_price,
        "thumbnail_url": p.thumbnail_url, "stock": p.stock,
        "is_time_sale": p.is_time_sale, "time_sale_price": p.time_sale_price,
        "time_sale_end": str(p.time_sale_end) if p.time_sale_end else None,
    }
