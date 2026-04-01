from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.cache.cache_service import CacheService
from app.infrastructure.persistence.models import OrderModel, UserModel


@dataclass
class DashboardResult:
    mau: int
    total_sales_today: int
    total_orders_today: int
    pending_orders: int


class GetDashboardUseCase:
    def __init__(self, session: AsyncSession, cache: CacheService):
        self._session = session
        self._cache = cache

    async def execute(self) -> DashboardResult:
        now = datetime.utcnow()
        year_month = now.strftime("%Y-%m")
        mau = await self._cache.get_mau(year_month)

        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        sales_q = select(func.coalesce(func.sum(OrderModel.final_amount), 0)).where(
            OrderModel.status.in_(["paid", "preparing", "shipping", "delivered", "confirmed"]),
            OrderModel.created_at >= today_start,
        )
        order_count_q = select(func.count()).select_from(OrderModel).where(
            OrderModel.created_at >= today_start
        )
        pending_q = select(func.count()).select_from(OrderModel).where(
            OrderModel.status == "pending"
        )

        total_sales_today = await self._session.scalar(sales_q) or 0
        total_orders_today = await self._session.scalar(order_count_q) or 0
        pending_orders = await self._session.scalar(pending_q) or 0

        return DashboardResult(
            mau=mau,
            total_sales_today=total_sales_today,
            total_orders_today=total_orders_today,
            pending_orders=pending_orders,
        )
