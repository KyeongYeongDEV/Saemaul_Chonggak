from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from app.domain.order.exceptions import InvalidOrderStatusException


class OrderStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    PREPARING = "preparing"
    SHIPPING = "shipping"
    DELIVERED = "delivered"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    EXCHANGE_REQUESTED = "exchange_requested"
    RETURN_REQUESTED = "return_requested"


@dataclass
class OrderItem:
    id: int | None
    order_id: int | None
    product_id: int
    product_name: str
    price: int
    quantity: int
    subtotal: int


@dataclass
class Order:
    id: int | None
    order_no: str
    user_id: int
    status: OrderStatus
    items: list[OrderItem]
    total_amount: int
    discount_amount: int
    shipping_fee: int
    final_amount: int
    coupon_id: int | None
    point_used: int
    receiver_name: str
    receiver_phone: str
    zipcode: str
    address1: str
    address2: str | None
    memo: str | None
    created_at: datetime
    updated_at: datetime | None = None

    def cancel(self) -> None:
        if self.status not in (OrderStatus.PENDING, OrderStatus.PAID):
            raise InvalidOrderStatusException("결제 대기 또는 결제 완료 상태에서만 취소할 수 있습니다.")
        self.status = OrderStatus.CANCELLED

    def request_exchange(self) -> None:
        if self.status != OrderStatus.DELIVERED:
            raise InvalidOrderStatusException("배송 완료 상태에서만 교환 신청이 가능합니다.")
        self.status = OrderStatus.EXCHANGE_REQUESTED

    def request_return(self) -> None:
        if self.status not in (OrderStatus.DELIVERED, OrderStatus.CONFIRMED):
            raise InvalidOrderStatusException("배송 완료 또는 구매 확정 상태에서만 반품 신청이 가능합니다.")
        self.status = OrderStatus.RETURN_REQUESTED
