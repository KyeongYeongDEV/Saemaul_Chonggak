from abc import ABC, abstractmethod

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
