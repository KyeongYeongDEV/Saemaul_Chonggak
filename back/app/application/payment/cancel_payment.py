from dataclasses import dataclass
from datetime import datetime

from app.core.exceptions import ForbiddenError, OrderNotFoundError
from app.domain.order.entities import OrderStatus
from app.domain.order.repository import OrderRepository
from app.domain.payment.entities import PaymentStatus
from app.domain.payment.repository import PaymentRepository
from app.infrastructure.payment.toss_adapter import TossPaymentAdapter


@dataclass
class CancelPaymentCommand:
    order_id: int
    user_id: int
    cancel_reason: str


class CancelPaymentUseCase:
    def __init__(
        self,
        payment_repo: PaymentRepository,
        order_repo: OrderRepository,
        toss_adapter: TossPaymentAdapter,
    ):
        self._payment_repo = payment_repo
        self._order_repo = order_repo
        self._toss = toss_adapter

    async def execute(self, cmd: CancelPaymentCommand) -> None:
        order = await self._order_repo.get_by_id(cmd.order_id)
        if not order or order.user_id != cmd.user_id:
            raise OrderNotFoundError()

        order.cancel()

        payment = await self._payment_repo.get_by_order_id(order.id)
        if payment and payment.payment_key and payment.status == PaymentStatus.DONE:
            await self._toss.cancel(payment.payment_key, cmd.cancel_reason)
            payment.status = PaymentStatus.CANCELLED
            payment.cancelled_at = datetime.utcnow()
            payment.cancel_reason = cmd.cancel_reason
            await self._payment_repo.update(payment)

        await self._order_repo.update(order)
