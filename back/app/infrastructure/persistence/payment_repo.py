from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.payment.entities import Payment, PaymentStatus
from app.domain.payment.repository import PaymentRepository
from app.infrastructure.persistence.models import PaymentModel


def _to_payment(m: PaymentModel) -> Payment:
    return Payment(
        id=m.id, order_id=m.order_id, order_no=m.order_no,
        payment_key=m.payment_key, method=m.method, status=PaymentStatus(m.status),
        amount=m.amount, approved_at=m.approved_at, cancelled_at=m.cancelled_at,
        cancel_reason=m.cancel_reason, raw_response=m.raw_response, created_at=m.created_at,
    )


class SQLPaymentRepository(PaymentRepository):
    def __init__(self, session: AsyncSession):
        self._s = session

    async def get_by_id(self, payment_id: int) -> Payment | None:
        m = await self._s.get(PaymentModel, payment_id)
        return _to_payment(m) if m else None

    async def get_by_order_id(self, order_id: int) -> Payment | None:
        result = await self._s.execute(select(PaymentModel).where(PaymentModel.order_id == order_id))
        m = result.scalar_one_or_none()
        return _to_payment(m) if m else None

    async def get_by_order_no(self, order_no: str) -> Payment | None:
        result = await self._s.execute(select(PaymentModel).where(PaymentModel.order_no == order_no))
        m = result.scalar_one_or_none()
        return _to_payment(m) if m else None

    async def list_by_user(self, user_id: int, page: int, size: int) -> tuple[list[Payment], int]:
        from app.infrastructure.persistence.models import OrderModel
        q = (
            select(PaymentModel)
            .join(OrderModel, PaymentModel.order_id == OrderModel.id)
            .where(OrderModel.user_id == user_id)
            .order_by(PaymentModel.created_at.desc())
            .offset((page - 1) * size)
            .limit(size)
        )
        count_q = (
            select(func.count())
            .select_from(PaymentModel)
            .join(OrderModel, PaymentModel.order_id == OrderModel.id)
            .where(OrderModel.user_id == user_id)
        )
        result = await self._s.execute(q)
        total = await self._s.scalar(count_q)
        return [_to_payment(m) for m in result.scalars()], total or 0

    async def save(self, payment: Payment) -> Payment:
        m = PaymentModel(
            order_id=payment.order_id, order_no=payment.order_no,
            payment_key=payment.payment_key, method=payment.method,
            status=payment.status.value, amount=payment.amount,
        )
        self._s.add(m)
        await self._s.flush()
        await self._s.refresh(m)
        return _to_payment(m)

    async def update(self, payment: Payment) -> Payment:
        await self._s.execute(
            update(PaymentModel).where(PaymentModel.id == payment.id).values(
                payment_key=payment.payment_key, method=payment.method,
                status=payment.status.value, approved_at=payment.approved_at,
                cancelled_at=payment.cancelled_at, cancel_reason=payment.cancel_reason,
                raw_response=payment.raw_response,
            )
        )
        return payment
