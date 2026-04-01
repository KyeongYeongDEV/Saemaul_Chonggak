from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.review.entities import Review
from app.domain.review.repository import ReviewRepository
from app.infrastructure.persistence.models import ReviewModel


def _to_review(m: ReviewModel) -> Review:
    return Review(
        id=m.id, user_id=m.user_id, product_id=m.product_id,
        order_id=m.order_id, rating=m.rating, content=m.content, created_at=m.created_at,
    )


class SQLReviewRepository(ReviewRepository):
    def __init__(self, session: AsyncSession):
        self._s = session

    async def get_by_order_product(self, order_id: int, product_id: int) -> Review | None:
        result = await self._s.execute(
            select(ReviewModel).where(
                ReviewModel.order_id == order_id, ReviewModel.product_id == product_id
            )
        )
        m = result.scalar_one_or_none()
        return _to_review(m) if m else None

    async def list_by_product(self, product_id: int, page: int, size: int) -> tuple[list[Review], int]:
        q = (
            select(ReviewModel)
            .where(ReviewModel.product_id == product_id)
            .order_by(ReviewModel.created_at.desc())
            .offset((page - 1) * size)
            .limit(size)
        )
        count_q = select(func.count()).select_from(ReviewModel).where(ReviewModel.product_id == product_id)
        result = await self._s.execute(q)
        total = await self._s.scalar(count_q)
        return [_to_review(m) for m in result.scalars()], total or 0

    async def save(self, review: Review) -> Review:
        m = ReviewModel(
            user_id=review.user_id, product_id=review.product_id,
            order_id=review.order_id, rating=review.rating, content=review.content,
        )
        self._s.add(m)
        await self._s.flush()
        await self._s.refresh(m)
        return _to_review(m)
