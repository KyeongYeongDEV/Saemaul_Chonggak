from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.persistence.models import FaqModel


@dataclass
class FaqItem:
    id: int
    category: str
    question: str
    answer: str
    sort_order: int


class ListFaqsUseCase:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def execute(self) -> list[FaqItem]:
        result = await self._session.execute(
            select(FaqModel).where(FaqModel.is_active == True).order_by(FaqModel.sort_order)
        )
        return [
            FaqItem(id=m.id, category=m.category, question=m.question, answer=m.answer, sort_order=m.sort_order)
            for m in result.scalars()
        ]
