from dataclasses import dataclass
from datetime import datetime, timezone

from app.domain.order.repository import OrderRepository
from app.infrastructure.cache.cache_service import CacheService


@dataclass
class DashboardResult:
    mau: int
    total_sales_today: int
    total_orders_today: int
    pending_orders: int


_PAID_STATUSES = ["paid", "preparing", "shipping", "delivered", "confirmed"]


class GetDashboardUseCase:
    def __init__(self, order_repo: OrderRepository, cache: CacheService):
        self._order_repo = order_repo
        self._cache = cache

    async def execute(self) -> DashboardResult:
        now = datetime.now(timezone.utc)
        year_month = now.strftime("%Y-%m")
        mau = await self._cache.get_mau(year_month)

        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        total_sales_today = await self._order_repo.sum_sales_since(today_start, _PAID_STATUSES)
        total_orders_today = await self._order_repo.count_since(today_start)
        pending_orders = await self._order_repo.count_by_status("pending")

        return DashboardResult(
            mau=mau,
            total_sales_today=total_sales_today,
            total_orders_today=total_orders_today,
            pending_orders=pending_orders,
        )
