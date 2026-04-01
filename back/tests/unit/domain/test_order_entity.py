import pytest
from datetime import datetime

from app.domain.order.entities import Order, OrderItem, OrderStatus
from app.domain.order.exceptions import InvalidOrderStatusException


def _make_order(status: OrderStatus) -> Order:
    return Order(
        id=1, order_no="20260401-TEST", user_id=1, status=status,
        items=[], total_amount=10000, discount_amount=0, shipping_fee=0, final_amount=10000,
        coupon_id=None, point_used=0, receiver_name="홍길동", receiver_phone="010-1234-5678",
        zipcode="12345", address1="서울시", address2=None, memo=None, created_at=datetime.utcnow(),
    )


def test_cancel_from_pending():
    order = _make_order(OrderStatus.PENDING)
    order.cancel()
    assert order.status == OrderStatus.CANCELLED


def test_cancel_from_paid():
    order = _make_order(OrderStatus.PAID)
    order.cancel()
    assert order.status == OrderStatus.CANCELLED


def test_cancel_from_shipping_fails():
    order = _make_order(OrderStatus.SHIPPING)
    with pytest.raises(InvalidOrderStatusException):
        order.cancel()


def test_exchange_from_delivered():
    order = _make_order(OrderStatus.DELIVERED)
    order.request_exchange()
    assert order.status == OrderStatus.EXCHANGE_REQUESTED


def test_exchange_from_pending_fails():
    order = _make_order(OrderStatus.PENDING)
    with pytest.raises(InvalidOrderStatusException):
        order.request_exchange()
