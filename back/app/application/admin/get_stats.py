from dataclasses import dataclass
from datetime import datetime, timezone, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.persistence.models import OrderModel, PaymentModel


@dataclass
class StatsResult:
    daily_sales: list[dict]
    total_revenue: int
    total_orders: int


class GetStatsUseCase:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def execute(self, days: int = 7) -> StatsResult:
        start = datetime.now(timezone.utc) - timedelta(days=days)

        # 일별 매출
        daily_q = (
            select(
                func.date(OrderModel.created_at).label("date"),
                func.count(OrderModel.id).label("orders"),
                func.coalesce(func.sum(OrderModel.final_amount), 0).label("revenue"),
            )
            .where(
                OrderModel.created_at >= start,
                OrderModel.status.notin_(["pending", "cancelled"]),
            )
            .group_by(func.date(OrderModel.created_at))
            .order_by(func.date(OrderModel.created_at))
        )
        result = await self._session.execute(daily_q)
        daily_sales = [{"date": str(r.date), "orders": r.orders, "revenue": r.revenue} for r in result]

        total_revenue_q = select(func.coalesce(func.sum(OrderModel.final_amount), 0)).where(
            OrderModel.status.notin_(["pending", "cancelled"])
        )
        total_orders_q = select(func.count()).select_from(OrderModel).where(
            OrderModel.status.notin_(["pending", "cancelled"])
        )
        total_revenue = await self._session.scalar(total_revenue_q) or 0
        total_orders = await self._session.scalar(total_orders_q) or 0

        return StatsResult(daily_sales=daily_sales, total_revenue=total_revenue, total_orders=total_orders)
