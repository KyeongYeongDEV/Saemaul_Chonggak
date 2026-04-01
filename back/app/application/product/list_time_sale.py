from app.domain.product.entities import Product
from app.domain.product.repository import ProductRepository


class ListTimeSaleUseCase:
    def __init__(self, product_repo: ProductRepository):
        self._repo = product_repo

    async def execute(self) -> list[Product]:
        return await self._repo.list_time_sale()
