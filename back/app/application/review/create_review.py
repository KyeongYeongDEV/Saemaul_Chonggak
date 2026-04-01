from dataclasses import dataclass
from datetime import datetime

from app.core.exceptions import AlreadyReviewedError, ForbiddenError, OrderNotFoundError
from app.domain.order.entities import OrderStatus
from app.domain.order.repository import OrderRepository
from app.domain.review.entities import Review
from app.domain.review.exceptions import AlreadyReviewedException
from app.domain.review.repository import ReviewRepository


@dataclass
class CreateReviewCommand:
    user_id: int
    order_id: int
    product_id: int
    rating: int
    content: str | None


class CreateReviewUseCase:
    def __init__(self, order_repo: OrderRepository, review_repo: ReviewRepository):
        self._order_repo = order_repo
        self._review_repo = review_repo

    async def execute(self, cmd: CreateReviewCommand) -> Review:
        order = await self._order_repo.get_by_id(cmd.order_id)
        if not order or order.user_id != cmd.user_id:
            raise ForbiddenError()
        if order.status not in (OrderStatus.DELIVERED, OrderStatus.CONFIRMED):
            raise ForbiddenError("배송 완료 후 리뷰를 작성할 수 있습니다.")

        # 주문 내 해당 상품 확인
        has_product = any(item.product_id == cmd.product_id for item in order.items)
        if not has_product:
            raise ForbiddenError("해당 주문에 없는 상품입니다.")

        existing = await self._review_repo.get_by_order_product(cmd.order_id, cmd.product_id)
        if existing:
            raise AlreadyReviewedError()

        review = Review(
            id=None, user_id=cmd.user_id, product_id=cmd.product_id,
            order_id=cmd.order_id, rating=cmd.rating, content=cmd.content,
            created_at=datetime.utcnow(),
        )
        return await self._review_repo.save(review)
