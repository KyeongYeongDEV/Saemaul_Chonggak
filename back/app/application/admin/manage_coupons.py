from dataclasses import dataclass
from datetime import datetime, timezone

from app.domain.coupon.entities import Coupon, CouponType
from app.domain.coupon.repository import CouponRepository
from app.infrastructure.cache.cache_service import CacheService
from app.infrastructure.persistence.audit_log_repo import AuditLogRepository


@dataclass
class CreateCouponCommand:
    code: str
    name: str
    type: str
    discount_value: int
    min_order_amount: int
    max_discount: int | None
    total_stock: int
    started_at: datetime
    expired_at: datetime
    admin_id: int
    ip_address: str | None


class AdminCouponUseCase:
    def __init__(
        self,
        coupon_repo: CouponRepository,
        audit_repo: AuditLogRepository,
        cache: CacheService,
    ):
        self._repo = coupon_repo
        self._audit = audit_repo
        self._cache = cache

    async def list(self, page: int, size: int):
        coupons, total = await self._repo.list_all(page, size)
        return coupons, total

    async def create(self, cmd: CreateCouponCommand) -> Coupon:
        coupon = Coupon(
            id=None, code=cmd.code, name=cmd.name, type=CouponType(cmd.type),
            discount_value=cmd.discount_value, min_order_amount=cmd.min_order_amount,
            max_discount=cmd.max_discount, total_stock=cmd.total_stock, issued_count=0,
            started_at=cmd.started_at, expired_at=cmd.expired_at, is_active=True,
            created_at=datetime.now(timezone.utc),
        )
        saved = await self._repo.save(coupon)
        # Redis에 재고 초기화
        ttl = int((cmd.expired_at - datetime.now(timezone.utc)).total_seconds())
        if ttl > 0:
            await self._cache.init_stock(f"coupon:stock:{cmd.code}", cmd.total_stock, ttl)
        await self._audit.write(
            admin_id=cmd.admin_id, action="CREATE_COUPON",
            target_type="coupon", target_id=saved.id, ip_address=cmd.ip_address,
        )
        return saved

    async def delete(self, coupon_id: int, admin_id: int, ip_address: str | None) -> None:
        await self._repo.delete(coupon_id)
        await self._audit.write(
            admin_id=admin_id, action="DELETE_COUPON",
            target_type="coupon", target_id=coupon_id, ip_address=ip_address,
        )
