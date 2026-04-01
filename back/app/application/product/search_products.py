from dataclasses import dataclass

from app.domain.product.entities import Product
from app.domain.product.repository import ProductRepository


@dataclass
class SearchResult:
    items: list[Product]
    total: int
    page: int
    size: int


class SearchProductsUseCase:
    def __init__(self, product_repo: ProductRepository):
        self._repo = product_repo

    async def execute(self, query: str, page: int, size: int) -> SearchResult:
        items, total = await self._repo.search(query, page, size)
        return SearchResult(items=items, total=total, page=page, size=size)
