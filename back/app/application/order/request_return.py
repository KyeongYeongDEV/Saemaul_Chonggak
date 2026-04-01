from dataclasses import dataclass

from app.core.exceptions import ForbiddenError, InvalidOrderStatusError, OrderNotFoundError
from app.domain.order.exceptions import InvalidOrderStatusException
from app.domain.order.repository import OrderRepository


@dataclass
class RequestReturnCommand:
    order_id: int
    user_id: int
    reason: str


class RequestReturnUseCase:
    def __init__(self, order_repo: OrderRepository):
        self._repo = order_repo

    async def execute(self, cmd: RequestReturnCommand) -> None:
        order = await self._repo.get_by_id(cmd.order_id)
        if not order:
            raise OrderNotFoundError()
        if order.user_id != cmd.user_id:
            raise ForbiddenError()
        try:
            order.request_return()
        except InvalidOrderStatusException as e:
            raise InvalidOrderStatusError(e.message)
        await self._repo.update(order)
