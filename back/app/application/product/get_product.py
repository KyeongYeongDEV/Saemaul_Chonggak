from app.core.exceptions import ProductNotFoundError
from app.domain.product.entities import Product
from app.domain.product.repository import ProductRepository
from app.infrastructure.cache.cache_service import CacheService


class GetProductUseCase:
    def __init__(self, product_repo: ProductRepository, cache: CacheService):
        self._repo = product_repo
        self._cache = cache

    async def execute(self, product_id: int) -> Product:
        async def load():
            product = await self._repo.get_by_id(product_id)
            if not product:
                return None
            return {
                "id": product.id, "category_id": product.category_id,
                "name": product.name, "description": product.description,
                "price": product.price, "sale_price": product.sale_price,
                "stock": product.stock, "thumbnail_url": product.thumbnail_url,
                "is_active": product.is_active, "is_time_sale": product.is_time_sale,
                "time_sale_start": str(product.time_sale_start) if product.time_sale_start else None,
                "time_sale_end": str(product.time_sale_end) if product.time_sale_end else None,
                "time_sale_price": product.time_sale_price, "time_sale_stock": product.time_sale_stock,
                "created_at": str(product.created_at),
                "images": [{"id": i.id, "url": i.url, "sort_order": i.sort_order} for i in product.images],
            }

        data = await self._cache.get_or_set(f"product:detail:{product_id}", 600, load)
        if data is None:
            raise ProductNotFoundError()
        return data
