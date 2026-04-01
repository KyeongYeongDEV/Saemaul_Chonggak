from dataclasses import dataclass
from datetime import datetime, timezone

from app.core.exceptions import CouponExpiredError, CouponNotFoundError, CouponOutOfStockError, ValidationError
from app.domain.coupon.entities import UserCoupon
from app.domain.coupon.repository import CouponRepository, UserCouponRepository
from app.infrastructure.cache.cache_service import CacheService


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
            raise ValidationError("이미 발급받은 쿠폰입니다.")

        # Redis 원자적 재고 감소 (Lua Script — DECR only if > 0)
        stock_key = f"coupon:stock:{coupon.code}"
        result = await self._cache.atomic_decr_stock(stock_key)
        if result < 0:
            raise CouponOutOfStockError()

        # DB insert — UniqueConstraint(user_id, coupon_id)가 동시 요청 중복 방어
        # insert 실패(IntegrityError) 시 Redis 재고 복구
        try:
            user_coupon = UserCoupon(
                id=None, user_id=cmd.user_id, coupon_id=coupon.id,
                is_used=False, used_at=None, order_id=None,
                created_at=datetime.now(timezone.utc),
            )
            saved = await self._user_coupon_repo.save(user_coupon)
        except Exception:
            # DB 실패 시 Redis 재고 원상복구
            await self._cache.init_stock(
                stock_key,
                result + 1,  # 감소 전 값으로 복구
                int((coupon.expired_at - datetime.now(timezone.utc)).total_seconds()),
            )
            raise ValidationError("쿠폰 발급 중 오류가 발생했습니다.")

        # issued_count는 DB 레벨 atomic increment가 이상적이나
        # 현재 구조에서는 flush 후 갱신 (동시성 이슈는 Redis 재고로 1차 방어)
        coupon.issued_count += 1
        await self._coupon_repo.update(coupon)

        return saved
