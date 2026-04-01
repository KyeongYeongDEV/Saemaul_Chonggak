from abc import ABC, abstractmethod

from app.domain.coupon.entities import Coupon, UserCoupon


class CouponRepository(ABC):
    @abstractmethod
    async def get_by_id(self, coupon_id: int) -> Coupon | None: ...

    @abstractmethod
    async def get_by_code(self, code: str) -> Coupon | None: ...

    @abstractmethod
    async def list_all(self, page: int, size: int) -> tuple[list[Coupon], int]: ...

    @abstractmethod
    async def save(self, coupon: Coupon) -> Coupon: ...

    @abstractmethod
    async def update(self, coupon: Coupon) -> Coupon: ...

    @abstractmethod
    async def delete(self, coupon_id: int) -> None: ...


class UserCouponRepository(ABC):
    @abstractmethod
    async def get(self, user_id: int, coupon_id: int) -> UserCoupon | None: ...

    @abstractmethod
    async def list_by_user(self, user_id: int) -> list[UserCoupon]: ...

    @abstractmethod
    async def save(self, user_coupon: UserCoupon) -> UserCoupon: ...

    @abstractmethod
    async def mark_used(self, user_coupon_id: int, order_id: int) -> None: ...
