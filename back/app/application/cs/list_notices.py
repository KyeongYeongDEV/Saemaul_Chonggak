from dataclasses import dataclass

from app.domain.cs.repository import NoticeRepository


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
    def __init__(self, notice_repo: NoticeRepository):
        self._repo = notice_repo

    async def execute(self, page: int, size: int) -> NoticeListResult:
        notices, total = await self._repo.list_active(page, size)
        items = [
            NoticeItem(
                id=n.id,
                title=n.title,
                content=n.content,
                is_pinned=n.is_pinned,
                created_at=str(n.created_at),
            )
            for n in notices
        ]
        return NoticeListResult(items=items, total=total)
