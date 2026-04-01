from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.coupon.claim_coupon import ClaimCouponCommand, ClaimCouponUseCase
from app.application.coupon.list_coupons import ListCouponsUseCase
from app.core.dependencies import get_current_user_id
from app.infrastructure.cache.cache_service import CacheService
from app.infrastructure.cache.redis_client import get_redis
from app.infrastructure.persistence.coupon_repo import SQLCouponRepository, SQLUserCouponRepository
from app.infrastructure.persistence.database import get_db
from app.presentation.schemas.common import ApiResponse

router = APIRouter(prefix="/coupons", tags=["Coupons"])


@router.get("/me", response_model=ApiResponse[list[dict]])
async def my_coupons(user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    coupons = await ListCouponsUseCase(SQLUserCouponRepository(db)).execute(user_id)
    return ApiResponse(data=[
        {
            "id": uc.coupon_id,
            "user_coupon_id": uc.id,
            "name": uc.coupon.name if uc.coupon else None,
            "type": uc.coupon.type.value if uc.coupon else None,
            "discount_value": uc.coupon.discount_value if uc.coupon else None,
            "is_used": uc.is_used,
            "expired_at": str(uc.coupon.expired_at) if uc.coupon else None,
        }
        for uc in coupons
    ])


@router.post("/claim")
async def claim_coupon(
    code: str,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    use_case = ClaimCouponUseCase(
        SQLCouponRepository(db), SQLUserCouponRepository(db), CacheService(redis)
    )
    await use_case.execute(ClaimCouponCommand(user_id=user_id, coupon_code=code))
    return ApiResponse(data={"message": "쿠폰이 발급되었습니다."})
