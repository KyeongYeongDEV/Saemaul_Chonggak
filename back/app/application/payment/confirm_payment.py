from dataclasses import dataclass
from datetime import datetime

from app.core.exceptions import AmountMismatchError, OrderNotFoundError, PaymentFailedError
from app.domain.order.entities import OrderStatus
from app.domain.order.repository import OrderRepository
from app.domain.payment.entities import PaymentStatus
from app.domain.payment.exceptions import AmountMismatchException
from app.domain.payment.repository import PaymentRepository
from app.domain.user.repository import UserRepository
from app.infrastructure.cache.cache_service import CacheService
from app.infrastructure.payment.toss_adapter import TossPaymentAdapter


@dataclass
class ConfirmPaymentCommand:
    payment_key: str
    order_no: str
    amount: int


@dataclass
class ConfirmPaymentResult:
    order_no: str
    amount: int
    method: str | None


class ConfirmPaymentUseCase:
    def __init__(
        self,
        payment_repo: PaymentRepository,
        order_repo: OrderRepository,
        user_repo: UserRepository,
        toss_adapter: TossPaymentAdapter,
        cart_cache: CacheService,
    ):
        self._payment_repo = payment_repo
        self._order_repo = order_repo
        self._user_repo = user_repo
        self._toss = toss_adapter
        self._cache = cart_cache

    async def execute(self, cmd: ConfirmPaymentCommand, user_id: int) -> ConfirmPaymentResult:
        # 1. DB에서 주문 조회 (클라이언트 금액 무시)
        order = await self._order_repo.get_by_order_no(cmd.order_no)
        if not order or order.user_id != user_id:
            raise OrderNotFoundError()

        payment = await self._payment_repo.get_by_order_id(order.id)
        if not payment:
            raise OrderNotFoundError()

        # 2. 금액 검증 (도메인 엔티티에서 처리)
        try:
            payment.verify_amount(cmd.amount)
        except AmountMismatchException:
            raise AmountMismatchError()

        # 3. 토스 결제 승인 API 호출
        raw = await self._toss.confirm(cmd.payment_key, cmd.order_no, payment.amount)

        # 4. 상태 업데이트
        payment.payment_key = cmd.payment_key
        payment.status = PaymentStatus.DONE
        payment.method = raw.get("method")
        payment.approved_at = datetime.utcnow()
        payment.raw_response = raw
        await self._payment_repo.update(payment)

        order.status = OrderStatus.PAID
        await self._order_repo.update(order)

        # 5. 장바구니 비우기
        from app.infrastructure.cache.cart_repo import RedisCartRepository
        await self._cache.invalidate(f"cart:{user_id}")

        # 6. 포인트 적립 (결제액의 1%)
        user = await self._user_repo.get_by_id(user_id)
        if user:
            user.earn_point(int(payment.amount * 0.01))
            await self._user_repo.update(user)

        return ConfirmPaymentResult(order_no=order.order_no, amount=payment.amount, method=payment.method)
