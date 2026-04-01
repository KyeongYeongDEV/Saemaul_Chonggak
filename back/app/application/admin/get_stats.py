from dataclasses import dataclass
from datetime import datetime, timezone, timedelta

from app.domain.order.repository import OrderRepository


@dataclass
class StatsResult:
    daily_sales: list[dict]
    total_revenue: int
    total_orders: int


_EXCLUDE_STATUSES = ["pending", "cancelled"]


class GetStatsUseCase:
    def __init__(self, order_repo: OrderRepository):
        self._order_repo = order_repo

    async def execute(self, days: int = 7) -> StatsResult:
        start = datetime.now(timezone.utc) - timedelta(days=days)

        daily_sales = await self._order_repo.daily_sales(start, _EXCLUDE_STATUSES)
        total_revenue = await self._order_repo.sum_total_revenue(_EXCLUDE_STATUSES)
        total_orders = await self._order_repo.count_total_orders(_EXCLUDE_STATUSES)

        return StatsResult(
            daily_sales=daily_sales,
            total_revenue=total_revenue,
            total_orders=total_orders,
        )
