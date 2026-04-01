from app.core.exceptions import ForbiddenError, OrderNotFoundError
from app.domain.order.entities import Order
from app.domain.order.repository import OrderRepository


class GetOrderUseCase:
    def __init__(self, order_repo: OrderRepository):
        self._repo = order_repo

    async def execute(self, order_id: int, user_id: int) -> Order:
        order = await self._repo.get_by_id(order_id)
        if not order:
            raise OrderNotFoundError()
        if order.user_id != user_id:
            raise ForbiddenError()
        return order
