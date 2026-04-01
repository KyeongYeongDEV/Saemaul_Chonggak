from dataclasses import dataclass
from datetime import datetime

from app.domain.payment.entities import Payment
from app.domain.payment.repository import PaymentRepository


@dataclass
class PaymentItem:
    id: int
    order_no: str
    payment_key: str | None
    method: str | None
    status: str
    amount: int
    approved_at: datetime | None
    created_at: datetime


@dataclass
class GetPaymentsResult:
    items: list[PaymentItem]
    total: int


class GetPaymentsUseCase:
    def __init__(self, payment_repo: PaymentRepository):
        self._repo = payment_repo

    async def execute(self, user_id: int, page: int, size: int) -> GetPaymentsResult:
        payments, total = await self._repo.list_by_user(user_id, page, size)
        items = [
            PaymentItem(
                id=p.id,
                order_no=p.order_no,
                payment_key=p.payment_key,
                method=p.method,
                status=p.status.value,
                amount=p.amount,
                approved_at=p.approved_at,
                created_at=p.created_at,
            )
            for p in payments
        ]
        return GetPaymentsResult(items=items, total=total)
