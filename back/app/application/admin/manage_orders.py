from dataclasses import dataclass

from app.core.exceptions import ForbiddenError, InvalidOrderStatusError, OrderNotFoundError
from app.domain.order.entities import OrderStatus
from app.domain.order.exceptions import InvalidOrderStatusException
from app.domain.order.repository import OrderRepository
from app.infrastructure.persistence.audit_log_repo import AuditLogRepository


@dataclass
class UpdateOrderStatusCommand:
    order_id: int
    new_status: str
    admin_id: int
    ip_address: str | None


class AdminOrderUseCase:
    def __init__(self, order_repo: OrderRepository, audit_repo: AuditLogRepository):
        self._order_repo = order_repo
        self._audit = audit_repo

    async def update_status(self, cmd: UpdateOrderStatusCommand) -> None:
        order = await self._order_repo.get_by_id(cmd.order_id)
        if not order:
            raise OrderNotFoundError()

        try:
            new_status = OrderStatus(cmd.new_status)
        except ValueError:
            raise InvalidOrderStatusError(f"잘못된 상태값: {cmd.new_status}")

        before = {"status": order.status.value}
        order.status = new_status
        await self._order_repo.update(order)

        await self._audit.write(
            admin_id=cmd.admin_id,
            action="UPDATE_ORDER_STATUS",
            target_type="order",
            target_id=order.id,
            before_data=before,
            after_data={"status": new_status.value},
            ip_address=cmd.ip_address,
        )
