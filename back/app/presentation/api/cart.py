from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.cart.add_to_cart import AddToCartCommand, AddToCartUseCase
from app.application.cart.get_cart import GetCartUseCase
from app.application.cart.remove_cart_item import RemoveCartItemCommand, RemoveCartItemUseCase
from app.application.cart.update_cart_item import UpdateCartItemCommand, UpdateCartItemUseCase
from app.core.dependencies import get_current_user_id
from app.infrastructure.cache.cart_repo import RedisCartRepository
from app.infrastructure.cache.redis_client import get_redis
from app.infrastructure.persistence.database import get_db
from app.infrastructure.persistence.product_repo import SQLProductRepository
from app.presentation.schemas.cart import AddToCartRequest, CartResponse, UpdateCartItemRequest
from app.presentation.schemas.common import ApiResponse

router = APIRouter(prefix="/cart", tags=["Cart"])


@router.get("", response_model=ApiResponse[CartResponse])
async def get_cart(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    result = await GetCartUseCase(RedisCartRepository(redis), SQLProductRepository(db)).execute(user_id)
    return ApiResponse(data=CartResponse(items=result.items, total_amount=result.total_amount, item_count=result.item_count))


@router.post("", status_code=201)
async def add_to_cart(
    body: AddToCartRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    await AddToCartUseCase(RedisCartRepository(redis), SQLProductRepository(db)).execute(
        AddToCartCommand(user_id=user_id, product_id=body.product_id, quantity=body.quantity)
    )
    return ApiResponse(data={"message": "장바구니에 추가되었습니다."})


@router.put("/{product_id}")
async def update_cart_item(
    product_id: int,
    body: UpdateCartItemRequest,
    user_id: int = Depends(get_current_user_id),
    redis=Depends(get_redis),
):
    await UpdateCartItemUseCase(RedisCartRepository(redis)).execute(
        UpdateCartItemCommand(user_id=user_id, product_id=product_id, quantity=body.quantity)
    )
    return ApiResponse(data={"message": "수량이 변경되었습니다."})


@router.delete("/{product_id}", status_code=204)
async def remove_cart_item(
    product_id: int,
    user_id: int = Depends(get_current_user_id),
    redis=Depends(get_redis),
):
    await RemoveCartItemUseCase(RedisCartRepository(redis)).execute(
        RemoveCartItemCommand(user_id=user_id, product_id=product_id)
    )


@router.delete("", status_code=204)
async def clear_cart(user_id: int = Depends(get_current_user_id), redis=Depends(get_redis)):
    await RemoveCartItemUseCase(RedisCartRepository(redis)).execute(
        RemoveCartItemCommand(user_id=user_id, product_id=None)
    )
