from abc import ABC, abstractmethod
from datetime import datetime

from app.domain.order.entities import Order


class OrderRepository(ABC):
    @abstractmethod
    async def get_by_id(self, order_id: int) -> Order | None: ...

    @abstractmethod
    async def get_by_order_no(self, order_no: str) -> Order | None: ...

    @abstractmethod
    async def list_by_user(
        self, user_id: int, page: int, size: int
    ) -> tuple[list[Order], int]: ...

    @abstractmethod
    async def list_all(
        self,
        page: int,
        size: int,
        status: str | None,
        start_date: str | None,
        end_date: str | None,
    ) -> tuple[list[Order], int]: ...

    @abstractmethod
    async def save(self, order: Order) -> Order: ...

    @abstractmethod
    async def update(self, order: Order) -> Order: ...

    @abstractmethod
    async def sum_sales_since(self, since: datetime, statuses: list[str]) -> int: ...

    @abstractmethod
    async def count_since(self, since: datetime) -> int: ...

    @abstractmethod
    async def count_by_status(self, status: str) -> int: ...

    @abstractmethod
    async def daily_sales(
        self, since: datetime, exclude_statuses: list[str]
    ) -> list[dict]: ...

    @abstractmethod
    async def sum_total_revenue(self, exclude_statuses: list[str]) -> int: ...

    @abstractmethod
    async def count_total_orders(self, exclude_statuses: list[str]) -> int: ...
