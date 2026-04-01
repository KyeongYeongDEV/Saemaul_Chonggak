from abc import ABC, abstractmethod

from app.domain.payment.entities import Payment


class PaymentRepository(ABC):
    @abstractmethod
    async def get_by_id(self, payment_id: int) -> Payment | None: ...

    @abstractmethod
    async def get_by_order_id(self, order_id: int) -> Payment | None: ...

    @abstractmethod
    async def get_by_order_no(self, order_no: str) -> Payment | None: ...

    @abstractmethod
    async def list_by_user(
        self, user_id: int, page: int, size: int
    ) -> tuple[list[Payment], int]: ...

    @abstractmethod
    async def save(self, payment: Payment) -> Payment: ...

    @abstractmethod
    async def update(self, payment: Payment) -> Payment: ...
