from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.order.cancel_order import CancelOrderCommand, CancelOrderUseCase
from app.application.order.get_order import GetOrderUseCase
from app.application.order.get_orders import GetOrdersUseCase
from app.application.order.request_exchange import RequestExchangeCommand, RequestExchangeUseCase
from app.application.order.request_return import RequestReturnCommand, RequestReturnUseCase
from app.core.dependencies import get_current_user_id
from app.infrastructure.persistence.database import get_db
from app.infrastructure.persistence.order_repo import SQLOrderRepository
from app.presentation.schemas.common import ApiResponse, PaginatedData
from app.presentation.schemas.order import CancelOrderRequest, ExchangeReturnRequest, OrderItemResponse, OrderResponse

router = APIRouter(prefix="/orders", tags=["Orders"])


def _order_to_response(order) -> OrderResponse:
    return OrderResponse(
        id=order.id, order_no=order.order_no, status=order.status.value,
        items=[OrderItemResponse(product_id=i.product_id, product_name=i.product_name, price=i.price, quantity=i.quantity, subtotal=i.subtotal) for i in order.items],
        total_amount=order.total_amount, discount_amount=order.discount_amount,
        shipping_fee=order.shipping_fee, final_amount=order.final_amount,
        receiver_name=order.receiver_name, receiver_phone=order.receiver_phone,
        zipcode=order.zipcode, address1=order.address1, address2=order.address2,
        memo=order.memo, created_at=str(order.created_at),
    )


@router.get("", response_model=ApiResponse[PaginatedData[OrderResponse]])
async def list_orders(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await GetOrdersUseCase(SQLOrderRepository(db)).execute(user_id, page, size)
    return ApiResponse(data=PaginatedData(
        items=[_order_to_response(o) for o in result.items],
        total=result.total, page=page, size=size,
    ))


@router.get("/{order_id}", response_model=ApiResponse[OrderResponse])
async def get_order(order_id: int, user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    order = await GetOrderUseCase(SQLOrderRepository(db)).execute(order_id, user_id)
    return ApiResponse(data=_order_to_response(order))


@router.post("/{order_id}/cancel", status_code=204)
async def cancel_order(
    order_id: int, body: CancelOrderRequest,
    user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db),
):
    await CancelOrderUseCase(SQLOrderRepository(db)).execute(
        CancelOrderCommand(order_id=order_id, user_id=user_id, reason=body.reason)
    )


@router.post("/{order_id}/exchange", status_code=204)
async def request_exchange(
    order_id: int, body: ExchangeReturnRequest,
    user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db),
):
    await RequestExchangeUseCase(SQLOrderRepository(db)).execute(
        RequestExchangeCommand(order_id=order_id, user_id=user_id, reason=body.reason)
    )


@router.post("/{order_id}/return", status_code=204)
async def request_return(
    order_id: int, body: ExchangeReturnRequest,
    user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db),
):
    await RequestReturnUseCase(SQLOrderRepository(db)).execute(
        RequestReturnCommand(order_id=order_id, user_id=user_id, reason=body.reason)
    )
