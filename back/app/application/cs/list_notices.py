from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.persistence.models import NoticeModel


@dataclass
class NoticeItem:
    id: int
    title: str
    content: str
    is_pinned: bool
    created_at: str


@dataclass
class NoticeListResult:
    items: list[NoticeItem]
    total: int


class ListNoticesUseCase:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def execute(self, page: int, size: int) -> NoticeListResult:
        q = (
            select(NoticeModel)
            .where(NoticeModel.is_active == True)
            .order_by(NoticeModel.is_pinned.desc(), NoticeModel.created_at.desc())
            .offset((page - 1) * size)
            .limit(size)
        )
        count_q = select(func.count()).select_from(NoticeModel).where(NoticeModel.is_active == True)
        result = await self._session.execute(q)
        total = await self._session.scalar(count_q)
        items = [
            NoticeItem(id=m.id, title=m.title, content=m.content, is_pinned=m.is_pinned, created_at=str(m.created_at))
            for m in result.scalars()
        ]
        return NoticeListResult(items=items, total=total or 0)
