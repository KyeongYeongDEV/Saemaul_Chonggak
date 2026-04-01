from datetime import datetime

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.order.entities import Order, OrderItem, OrderStatus
from app.domain.order.repository import OrderRepository
from app.infrastructure.persistence.models import OrderItemModel, OrderModel


def _to_order(m: OrderModel) -> Order:
    return Order(
        id=m.id,
        order_no=m.order_no,
        user_id=m.user_id,
        status=OrderStatus(m.status),
        items=[
            OrderItem(
                id=i.id, order_id=i.order_id, product_id=i.product_id,
                product_name=i.product_name, price=i.price, quantity=i.quantity, subtotal=i.subtotal,
            )
            for i in m.items
        ],
        total_amount=m.total_amount,
        discount_amount=m.discount_amount,
        shipping_fee=m.shipping_fee,
        final_amount=m.final_amount,
        coupon_id=m.coupon_id,
        point_used=m.point_used,
        receiver_name=m.receiver_name,
        receiver_phone=m.receiver_phone,
        zipcode=m.zipcode,
        address1=m.address1,
        address2=m.address2,
        memo=m.memo,
        created_at=m.created_at,
        updated_at=m.updated_at,
    )


class SQLOrderRepository(OrderRepository):
    def __init__(self, session: AsyncSession):
        self._s = session

    async def get_by_id(self, order_id: int) -> Order | None:
        result = await self._s.execute(
            select(OrderModel).options(selectinload(OrderModel.items)).where(OrderModel.id == order_id)
        )
        m = result.scalar_one_or_none()
        return _to_order(m) if m else None

    async def get_by_order_no(self, order_no: str) -> Order | None:
        result = await self._s.execute(
            select(OrderModel).options(selectinload(OrderModel.items)).where(OrderModel.order_no == order_no)
        )
        m = result.scalar_one_or_none()
        return _to_order(m) if m else None

    async def list_by_user(self, user_id: int, page: int, size: int) -> tuple[list[Order], int]:
        q = (
            select(OrderModel)
            .options(selectinload(OrderModel.items))
            .where(OrderModel.user_id == user_id)
            .order_by(OrderModel.created_at.desc())
            .offset((page - 1) * size)
            .limit(size)
        )
        count_q = select(func.count()).select_from(OrderModel).where(OrderModel.user_id == user_id)
        result = await self._s.execute(q)
        total = await self._s.scalar(count_q)
        return [_to_order(m) for m in result.scalars()], total or 0

    async def list_all(self, page, size, status, start_date, end_date) -> tuple[list[Order], int]:
        q = select(OrderModel).options(selectinload(OrderModel.items))
        count_q = select(func.count()).select_from(OrderModel)
        if status:
            q = q.where(OrderModel.status == status)
            count_q = count_q.where(OrderModel.status == status)
        if start_date:
            q = q.where(OrderModel.created_at >= start_date)
            count_q = count_q.where(OrderModel.created_at >= start_date)
        if end_date:
            q = q.where(OrderModel.created_at <= end_date)
            count_q = count_q.where(OrderModel.created_at <= end_date)
        q = q.order_by(OrderModel.created_at.desc()).offset((page - 1) * size).limit(size)
        result = await self._s.execute(q)
        total = await self._s.scalar(count_q)
        return [_to_order(m) for m in result.scalars()], total or 0

    async def save(self, order: Order) -> Order:
        m = OrderModel(
            order_no=order.order_no, user_id=order.user_id, status=order.status.value,
            total_amount=order.total_amount, discount_amount=order.discount_amount,
            shipping_fee=order.shipping_fee, final_amount=order.final_amount,
            coupon_id=order.coupon_id, point_used=order.point_used,
            receiver_name=order.receiver_name, receiver_phone=order.receiver_phone,
            zipcode=order.zipcode, address1=order.address1, address2=order.address2, memo=order.memo,
        )
        self._s.add(m)
        await self._s.flush()
        for item in order.items:
            im = OrderItemModel(
                order_id=m.id, product_id=item.product_id, product_name=item.product_name,
                price=item.price, quantity=item.quantity, subtotal=item.subtotal,
            )
            self._s.add(im)
        await self._s.flush()
        await self._s.refresh(m)
        return _to_order(m)

    async def update(self, order: Order) -> Order:
        await self._s.execute(
            update(OrderModel).where(OrderModel.id == order.id).values(status=order.status.value)
        )
        return order

    async def sum_sales_since(self, since: datetime, statuses: list[str]) -> int:
        q = select(func.coalesce(func.sum(OrderModel.final_amount), 0)).where(
            OrderModel.status.in_(statuses),
            OrderModel.created_at >= since,
        )
        return await self._s.scalar(q) or 0

    async def count_since(self, since: datetime) -> int:
        q = select(func.count()).select_from(OrderModel).where(OrderModel.created_at >= since)
        return await self._s.scalar(q) or 0

    async def count_by_status(self, status: str) -> int:
        q = select(func.count()).select_from(OrderModel).where(OrderModel.status == status)
        return await self._s.scalar(q) or 0

    async def daily_sales(self, since: datetime, exclude_statuses: list[str]) -> list[dict]:
        q = (
            select(
                func.date(OrderModel.created_at).label("date"),
                func.count(OrderModel.id).label("orders"),
                func.coalesce(func.sum(OrderModel.final_amount), 0).label("revenue"),
            )
            .where(
                OrderModel.created_at >= since,
                OrderModel.status.notin_(exclude_statuses),
            )
            .group_by(func.date(OrderModel.created_at))
            .order_by(func.date(OrderModel.created_at))
        )
        result = await self._s.execute(q)
        return [{"date": str(r.date), "orders": r.orders, "revenue": r.revenue} for r in result]

    async def sum_total_revenue(self, exclude_statuses: list[str]) -> int:
        q = select(func.coalesce(func.sum(OrderModel.final_amount), 0)).where(
            OrderModel.status.notin_(exclude_statuses)
        )
        return await self._s.scalar(q) or 0

    async def count_total_orders(self, exclude_statuses: list[str]) -> int:
        q = select(func.count()).select_from(OrderModel).where(
            OrderModel.status.notin_(exclude_statuses)
        )
        return await self._s.scalar(q) or 0
