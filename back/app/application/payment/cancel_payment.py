from dataclasses import dataclass
from datetime import datetime, timezone

from app.core.exceptions import ForbiddenError, OrderNotFoundError, PaymentFailedError
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

        payment = await self._payment_repo.get_by_order_id(order.id)

        # 결제 취소가 필요한 경우: 토스 환불 먼저, 성공 후 DB 업데이트
        if payment and payment.payment_key and payment.status == PaymentStatus.DONE:
            # 토스 환불 실패 시 예외 전파 → order 상태 변경 없음
            await self._toss.cancel(payment.payment_key, cmd.cancel_reason)

            now = datetime.now(timezone.utc)
            payment.status = PaymentStatus.CANCELLED
            payment.cancelled_at = now
            payment.cancel_reason = cmd.cancel_reason
            await self._payment_repo.update(payment)

        # 토스 환불 완료 후 주문 상태 변경
        order.cancel()
        await self._order_repo.update(order)
