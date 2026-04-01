from dataclasses import dataclass

from app.domain.cs.repository import FaqRepository


@dataclass
class FaqItem:
    id: int
    category: str
    question: str
    answer: str
    sort_order: int


class ListFaqsUseCase:
    def __init__(self, faq_repo: FaqRepository):
        self._repo = faq_repo

    async def execute(self) -> list[FaqItem]:
        faqs = await self._repo.list_active()
        return [
            FaqItem(
                id=f.id,
                category=f.category,
                question=f.question,
                answer=f.answer,
                sort_order=f.sort_order,
            )
            for f in faqs
        ]
