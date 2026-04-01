from dataclasses import dataclass
from datetime import datetime, timezone

from app.core.exceptions import ValidationError
from app.domain.cs.entities import Inquiry
from app.domain.cs.repository import InquiryRepository
from app.domain.order.repository import OrderRepository


@dataclass
class CreateInquiryCommand:
    user_id: int
    order_id: int | None
    title: str
    content: str


class CreateInquiryUseCase:
    def __init__(self, inquiry_repo: InquiryRepository, order_repo: OrderRepository):
        self._repo = inquiry_repo
        self._order_repo = order_repo

    async def execute(self, cmd: CreateInquiryCommand) -> int:
        if cmd.order_id is not None:
            order = await self._order_repo.get_by_id(cmd.order_id)
            if not order or order.user_id != cmd.user_id:
                raise ValidationError("주문을 찾을 수 없습니다.")

        inquiry = Inquiry(
            id=None,
            user_id=cmd.user_id,
            order_id=cmd.order_id,
            title=cmd.title,
            content=cmd.content,
            status="pending",
            answer=None,
            answered_at=None,
            created_at=datetime.now(timezone.utc),
        )
        saved = await self._repo.save(inquiry)
        return saved.id
