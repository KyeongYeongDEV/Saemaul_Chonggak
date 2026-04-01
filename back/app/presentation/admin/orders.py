from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.admin.manage_orders import AdminOrderUseCase, UpdateOrderStatusCommand
from app.core.dependencies import require_admin
from app.infrastructure.persistence.audit_log_repo import AuditLogRepository
from app.infrastructure.persistence.database import get_db
from app.infrastructure.persistence.order_repo import SQLOrderRepository
from app.presentation.schemas.common import ApiResponse, PaginatedData
from app.presentation.schemas.order import OrderResponse, OrderItemResponse
from pydantic import BaseModel

router = APIRouter(prefix="/admin/orders", tags=["Admin"])


class UpdateStatusRequest(BaseModel):
    status: str


def _order_to_response(order) -> dict:
    return {
        "id": order.id, "order_no": order.order_no, "status": order.status.value,
        "final_amount": order.final_amount, "created_at": str(order.created_at),
        "receiver_name": order.receiver_name,
    }


@router.get("", response_model=ApiResponse[PaginatedData[dict]])
async def list_orders(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    admin: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    orders, total = await SQLOrderRepository(db).list_all(page, size, status, start_date, end_date)
    return ApiResponse(data=PaginatedData(items=[_order_to_response(o) for o in orders], total=total, page=page, size=size))


@router.patch("/{order_id}/status", status_code=204)
async def update_order_status(
    order_id: int,
    body: UpdateStatusRequest,
    request: Request,
    admin: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    use_case = AdminOrderUseCase(SQLOrderRepository(db), AuditLogRepository(db))
    await use_case.update_status(UpdateOrderStatusCommand(
        order_id=order_id, new_status=body.status,
        admin_id=int(admin["sub"]), ip_address=request.client.host if request.client else None,
    ))
