from dataclasses import dataclass

from app.domain.review.entities import Review
from app.domain.review.repository import ReviewRepository


@dataclass
class ListReviewsResult:
    items: list[Review]
    total: int
    page: int
    size: int


class ListReviewsUseCase:
    def __init__(self, review_repo: ReviewRepository):
        self._repo = review_repo

    async def execute(self, product_id: int, page: int, size: int) -> ListReviewsResult:
        items, total = await self._repo.list_by_product(product_id, page, size)
        return ListReviewsResult(items=items, total=total, page=page, size=size)
