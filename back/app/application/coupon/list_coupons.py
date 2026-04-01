from app.domain.coupon.entities import UserCoupon
from app.domain.coupon.repository import UserCouponRepository


class ListCouponsUseCase:
    def __init__(self, user_coupon_repo: UserCouponRepository):
        self._repo = user_coupon_repo

    async def execute(self, user_id: int) -> list[UserCoupon]:
        return await self._repo.list_by_user(user_id)
