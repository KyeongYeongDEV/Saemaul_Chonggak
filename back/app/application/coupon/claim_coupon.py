from dataclasses import dataclass
from datetime import datetime

from app.core.exceptions import CouponExpiredError, CouponNotFoundError, CouponOutOfStockError
from app.core.exceptions import ValidationError
from app.domain.coupon.entities import UserCoupon
from app.domain.coupon.exceptions import AlreadyClaimedException
from app.domain.coupon.repository import CouponRepository, UserCouponRepository
from app.infrastructure.cache.cache_service import CacheService
from app.infrastructure.persistence.coupon_repo import SQLCouponRepository


@dataclass
class ClaimCouponCommand:
    user_id: int
    coupon_code: str


class ClaimCouponUseCase:
    def __init__(
        self,
        coupon_repo: CouponRepository,
        user_coupon_repo: UserCouponRepository,
        cache: CacheService,
    ):
        self._coupon_repo = coupon_repo
        self._user_coupon_repo = user_coupon_repo
        self._cache = cache

    async def execute(self, cmd: ClaimCouponCommand) -> UserCoupon:
        coupon = await self._coupon_repo.get_by_code(cmd.coupon_code)
        if not coupon:
            raise CouponNotFoundError()
        if not coupon.is_valid():
            raise CouponExpiredError()

        existing = await self._user_coupon_repo.get(cmd.user_id, coupon.id)
        if existing:
            from app.core.exceptions import ValidationError
            raise ValidationError("이미 발급받은 쿠폰입니다.")

        # Redis 원자적 재고 감소
        stock_key = f"coupon:stock:{coupon.code}"
        result = await self._cache.atomic_decr_stock(stock_key)
        if result < 0:
            raise CouponOutOfStockError()

        user_coupon = UserCoupon(
            id=None, user_id=cmd.user_id, coupon_id=coupon.id,
            is_used=False, used_at=None, order_id=None, created_at=datetime.utcnow(),
        )
        saved = await self._user_coupon_repo.save(user_coupon)
        await self._coupon_repo.update(
            type(coupon)(**{**coupon.__dict__, "issued_count": coupon.issued_count + 1})
        )
        return saved
