from datetime import datetime, timezone

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.coupon.entities import Coupon, CouponType, UserCoupon
from app.domain.coupon.repository import CouponRepository, UserCouponRepository
from app.infrastructure.persistence.models import CouponModel, UserCouponModel


def _to_coupon(m: CouponModel) -> Coupon:
    return Coupon(
        id=m.id, code=m.code, name=m.name, type=CouponType(m.type),
        discount_value=m.discount_value, min_order_amount=m.min_order_amount,
        max_discount=m.max_discount, total_stock=m.total_stock, issued_count=m.issued_count,
        started_at=m.started_at, expired_at=m.expired_at, is_active=m.is_active, created_at=m.created_at,
    )


def _to_user_coupon(m: UserCouponModel) -> UserCoupon:
    return UserCoupon(
        id=m.id, user_id=m.user_id, coupon_id=m.coupon_id,
        is_used=m.is_used, used_at=m.used_at, order_id=m.order_id, created_at=m.created_at,
        coupon=_to_coupon(m.coupon) if m.coupon else None,
    )


class SQLCouponRepository(CouponRepository):
    def __init__(self, session: AsyncSession):
        self._s = session

    async def get_by_id(self, coupon_id: int) -> Coupon | None:
        m = await self._s.get(CouponModel, coupon_id)
        return _to_coupon(m) if m else None

    async def get_by_code(self, code: str) -> Coupon | None:
        result = await self._s.execute(select(CouponModel).where(CouponModel.code == code))
        m = result.scalar_one_or_none()
        return _to_coupon(m) if m else None

    async def list_all(self, page: int, size: int) -> tuple[list[Coupon], int]:
        q = select(CouponModel).order_by(CouponModel.created_at.desc()).offset((page - 1) * size).limit(size)
        count_q = select(func.count()).select_from(CouponModel)
        result = await self._s.execute(q)
        total = await self._s.scalar(count_q)
        return [_to_coupon(m) for m in result.scalars()], total or 0

    async def save(self, coupon: Coupon) -> Coupon:
        m = CouponModel(
            code=coupon.code, name=coupon.name, type=coupon.type.value,
            discount_value=coupon.discount_value, min_order_amount=coupon.min_order_amount,
            max_discount=coupon.max_discount, total_stock=coupon.total_stock,
            started_at=coupon.started_at, expired_at=coupon.expired_at, is_active=coupon.is_active,
        )
        self._s.add(m)
        await self._s.flush()
        await self._s.refresh(m)
        return _to_coupon(m)

    async def update(self, coupon: Coupon) -> Coupon:
        await self._s.execute(
            update(CouponModel).where(CouponModel.id == coupon.id).values(
                name=coupon.name, is_active=coupon.is_active, issued_count=coupon.issued_count,
            )
        )
        return coupon

    async def delete(self, coupon_id: int) -> None:
        m = await self._s.get(CouponModel, coupon_id)
        if m:
            await self._s.delete(m)


class SQLUserCouponRepository(UserCouponRepository):
    def __init__(self, session: AsyncSession):
        self._s = session

    async def get(self, user_id: int, coupon_id: int) -> UserCoupon | None:
        result = await self._s.execute(
            select(UserCouponModel)
            .options(selectinload(UserCouponModel.coupon))
            .where(UserCouponModel.user_id == user_id, UserCouponModel.coupon_id == coupon_id)
        )
        m = result.scalar_one_or_none()
        return _to_user_coupon(m) if m else None

    async def list_by_user(self, user_id: int) -> list[UserCoupon]:
        result = await self._s.execute(
            select(UserCouponModel)
            .options(selectinload(UserCouponModel.coupon))
            .where(UserCouponModel.user_id == user_id)
            .order_by(UserCouponModel.created_at.desc())
        )
        return [_to_user_coupon(m) for m in result.scalars()]

    async def save(self, user_coupon: UserCoupon) -> UserCoupon:
        m = UserCouponModel(user_id=user_coupon.user_id, coupon_id=user_coupon.coupon_id)
        self._s.add(m)
        await self._s.flush()
        await self._s.refresh(m)
        return _to_user_coupon(m)

    async def mark_used(self, user_coupon_id: int, order_id: int) -> None:
        await self._s.execute(
            update(UserCouponModel).where(UserCouponModel.id == user_coupon_id).values(
                is_used=True, used_at=datetime.now(timezone.utc), order_id=order_id,
            )
        )
