from dataclasses import dataclass
from datetime import datetime, timezone

from app.domain.cs.entities import Inquiry
from app.domain.cs.repository import InquiryRepository


@dataclass
class CreateInquiryCommand:
    user_id: int
    order_id: int | None
    title: str
    content: str


class CreateInquiryUseCase:
    def __init__(self, inquiry_repo: InquiryRepository):
        self._repo = inquiry_repo

    async def execute(self, cmd: CreateInquiryCommand) -> int:
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
