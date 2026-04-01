from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum

from app.domain.coupon.exceptions import CouponExpiredException


class CouponType(str, Enum):
    FIXED = "fixed"
    PERCENT = "percent"


@dataclass
class Coupon:
    id: int | None
    code: str
    name: str
    type: CouponType
    discount_value: int
    min_order_amount: int
    max_discount: int | None
    total_stock: int
    issued_count: int
    started_at: datetime
    expired_at: datetime
    is_active: bool
    created_at: datetime

    def is_valid(self) -> bool:
        now = datetime.now(timezone.utc)
        return self.is_active and self.started_at <= now <= self.expired_at

    def calculate_discount(self, order_amount: int) -> int:
        if self.type == CouponType.FIXED:
            return min(self.discount_value, order_amount)
        discount = int(order_amount * self.discount_value / 100)
        if self.max_discount:
            discount = min(discount, self.max_discount)
        return discount


@dataclass
class UserCoupon:
    id: int | None
    user_id: int
    coupon_id: int
    is_used: bool
    used_at: datetime | None
    order_id: int | None
    created_at: datetime
    coupon: Coupon | None = None
