import pytest
from datetime import datetime

from app.domain.payment.entities import Payment, PaymentStatus
from app.domain.payment.exceptions import AmountMismatchException


def _make_payment(amount: int) -> Payment:
    return Payment(
        id=None, order_id=1, order_no="20260401-ABC", payment_key=None,
        method=None, status=PaymentStatus.READY, amount=amount,
        approved_at=None, cancelled_at=None, cancel_reason=None,
        raw_response=None, created_at=datetime.utcnow(),
    )


def test_verify_amount_success():
    payment = _make_payment(15000)
    payment.verify_amount(15000)  # 예외 없음


def test_verify_amount_mismatch():
    payment = _make_payment(15000)
    with pytest.raises(AmountMismatchException):
        payment.verify_amount(14999)


def test_verify_amount_mismatch_message():
    payment = _make_payment(15000)
    with pytest.raises(AmountMismatchException) as exc_info:
        payment.verify_amount(10000)
    assert exc_info.value.expected == 15000
    assert exc_info.value.received == 10000
