from dataclasses import dataclass
from datetime import datetime, timezone

from app.core.exceptions import AmountMismatchError, OrderNotFoundError
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

        # 2. 이중 결제 방어 — 이미 완료된 결제면 멱등성 응답
        if payment.status == PaymentStatus.DONE:
            return ConfirmPaymentResult(
                order_no=order.order_no, amount=payment.amount, method=payment.method
            )

        # 3. 금액 검증 (도메인 엔티티에서 처리) — 클라이언트 금액 절대 신뢰 금지
        try:
            payment.verify_amount(cmd.amount)
        except AmountMismatchException:
            raise AmountMismatchError()

        # 4. 토스 결제 승인 API 호출
        raw = await self._toss.confirm(cmd.payment_key, cmd.order_no, payment.amount)

        # 5. DB 상태 업데이트 (토스 성공 후 즉시)
        now = datetime.now(timezone.utc)
        payment.payment_key = cmd.payment_key
        payment.status = PaymentStatus.DONE
        payment.method = raw.get("method")
        payment.approved_at = now
        payment.raw_response = raw
        await self._payment_repo.update(payment)

        order.status = OrderStatus.PAID
        await self._order_repo.update(order)

        # 6. 장바구니 캐시 무효화
        await self._cache.invalidate(f"cart:{user_id}")

        # 7. 포인트 적립 (결제액의 1%)
        user = await self._user_repo.get_by_id(user_id)
        if user:
            user.earn_point(int(payment.amount * 0.01))
            await self._user_repo.update(user)

        return ConfirmPaymentResult(order_no=order.order_no, amount=payment.amount, method=payment.method)
