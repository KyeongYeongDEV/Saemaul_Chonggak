from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.persistence.models import InquiryModel


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
    def __init__(self, session: AsyncSession):
        self._session = session

    async def execute(self, user_id: int, page: int, size: int) -> InquiryListResult:
        q = (
            select(InquiryModel)
            .where(InquiryModel.user_id == user_id)
            .order_by(InquiryModel.created_at.desc())
            .offset((page - 1) * size)
            .limit(size)
        )
        count_q = select(func.count()).select_from(InquiryModel).where(InquiryModel.user_id == user_id)
        result = await self._session.execute(q)
        total = await self._session.scalar(count_q)
        items = [
            InquiryItem(id=m.id, title=m.title, status=m.status, answer=m.answer, created_at=str(m.created_at))
            for m in result.scalars()
        ]
        return InquiryListResult(items=items, total=total or 0)
