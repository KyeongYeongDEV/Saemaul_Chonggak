from dataclasses import dataclass

from app.domain.order.entities import Order
from app.domain.order.repository import OrderRepository


@dataclass
class GetOrdersResult:
    items: list[Order]
    total: int
    page: int
    size: int


class GetOrdersUseCase:
    def __init__(self, order_repo: OrderRepository):
        self._repo = order_repo

    async def execute(self, user_id: int, page: int, size: int) -> GetOrdersResult:
        items, total = await self._repo.list_by_user(user_id, page, size)
        return GetOrdersResult(items=items, total=total, page=page, size=size)
