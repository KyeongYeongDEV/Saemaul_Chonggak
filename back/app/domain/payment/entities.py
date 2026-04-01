from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum

from app.domain.payment.exceptions import AmountMismatchException


class PaymentStatus(str, Enum):
    READY = "ready"
    DONE = "done"
    CANCELLED = "cancelled"
    FAILED = "failed"


@dataclass
class Payment:
    id: int | None
    order_id: int
    order_no: str
    payment_key: str | None
    method: str | None
    status: PaymentStatus
    amount: int
    approved_at: datetime | None
    cancelled_at: datetime | None
    cancel_reason: str | None
    raw_response: dict | None
    created_at: datetime

    def verify_amount(self, client_amount: int) -> None:
        """금액 불일치 시 AmountMismatchException 발생."""
        if self.amount != client_amount:
            raise AmountMismatchException(expected=self.amount, received=client_amount)
