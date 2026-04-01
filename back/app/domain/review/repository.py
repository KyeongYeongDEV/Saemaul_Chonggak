from abc import ABC, abstractmethod

from app.domain.review.entities import Review


class ReviewRepository(ABC):
    @abstractmethod
    async def get_by_order_product(
        self, order_id: int, product_id: int
    ) -> Review | None: ...

    @abstractmethod
    async def list_by_product(
        self, product_id: int, page: int, size: int
    ) -> tuple[list[Review], int]: ...

    @abstractmethod
    async def save(self, review: Review) -> Review: ...
