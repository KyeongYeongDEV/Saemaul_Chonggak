from dataclasses import dataclass

from app.domain.cs.repository import InquiryRepository


@dataclass
class InquiryItem:
    id: int
    title: str
    status: str
    answer: str | None
    created_at: str


@dataclass
class InquiryListResult:
    items: list[InquiryItem]
    total: int


class ListInquiriesUseCase:
    def __init__(self, inquiry_repo: InquiryRepository):
        self._repo = inquiry_repo

    async def execute(self, user_id: int, page: int, size: int) -> InquiryListResult:
        inquiries, total = await self._repo.list_by_user(user_id, page, size)
        items = [
            InquiryItem(
                id=i.id,
                title=i.title,
                status=i.status,
                answer=i.answer,
                created_at=str(i.created_at),
            )
            for i in inquiries
        ]
        return InquiryListResult(items=items, total=total)
