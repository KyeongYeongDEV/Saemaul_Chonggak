from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.payment.cancel_payment import CancelPaymentCommand, CancelPaymentUseCase
from app.application.payment.confirm_payment import ConfirmPaymentCommand, ConfirmPaymentUseCase
from app.application.payment.prepare_payment import PreparePaymentCommand, PreparePaymentUseCase
from app.core.dependencies import get_current_user_id
from app.infrastructure.cache.cache_service import CacheService
from app.infrastructure.cache.cart_repo import RedisCartRepository
from app.infrastructure.cache.redis_client import get_redis
from app.infrastructure.payment.toss_adapter import TossPaymentAdapter
from app.infrastructure.persistence.coupon_repo import SQLUserCouponRepository
from app.infrastructure.persistence.database import get_db
from app.infrastructure.persistence.order_repo import SQLOrderRepository
from app.infrastructure.persistence.payment_repo import SQLPaymentRepository
from app.infrastructure.persistence.product_repo import SQLProductRepository
from app.infrastructure.persistence.user_repo import SQLUserAddressRepository, SQLUserRepository
from app.presentation.schemas.common import ApiResponse
from app.presentation.schemas.payment import (
    CancelPaymentRequest,
    ConfirmPaymentRequest,
    ConfirmPaymentResponse,
    PreparePaymentRequest,
    PreparePaymentResponse,
)

router = APIRouter(prefix="/payments", tags=["Payments"])
_toss = TossPaymentAdapter()


@router.post("/prepare", response_model=ApiResponse[PreparePaymentResponse])
async def prepare_payment(
    body: PreparePaymentRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    use_case = PreparePaymentUseCase(
        SQLUserRepository(db), SQLUserAddressRepository(db), SQLProductRepository(db),
        RedisCartRepository(redis), SQLOrderRepository(db), SQLPaymentRepository(db),
        SQLUserCouponRepository(db),
    )
    result = await use_case.execute(PreparePaymentCommand(
        user_id=user_id, address_id=body.address_id,
        coupon_id=body.coupon_id, point_use=body.point_use, memo=body.memo,
    ))
    return ApiResponse(data=PreparePaymentResponse(
        order_no=result.order_no, amount=result.amount, order_name=result.order_name
    ))


@router.post("/confirm", response_model=ApiResponse[ConfirmPaymentResponse])
async def confirm_payment(
    body: ConfirmPaymentRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    use_case = ConfirmPaymentUseCase(
        SQLPaymentRepository(db), SQLOrderRepository(db), SQLUserRepository(db),
        _toss, CacheService(redis),
    )
    result = await use_case.execute(
        ConfirmPaymentCommand(payment_key=body.payment_key, order_no=body.order_no, amount=body.amount),
        user_id=user_id,
    )
    return ApiResponse(data=ConfirmPaymentResponse(
        order_no=result.order_no, amount=result.amount, method=result.method
    ))


@router.post("/{order_id}/cancel", status_code=204)
async def cancel_payment(
    order_id: int,
    body: CancelPaymentRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    use_case = CancelPaymentUseCase(SQLPaymentRepository(db), SQLOrderRepository(db), _toss)
    await use_case.execute(CancelPaymentCommand(order_id=order_id, user_id=user_id, cancel_reason=body.cancel_reason))
