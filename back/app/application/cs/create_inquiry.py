from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.persistence.models import InquiryModel


@dataclass
class CreateInquiryCommand:
    user_id: int
    order_id: int | None
    title: str
    content: str


class CreateInquiryUseCase:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def execute(self, cmd: CreateInquiryCommand) -> int:
        m = InquiryModel(
            user_id=cmd.user_id, order_id=cmd.order_id,
            title=cmd.title, content=cmd.content,
        )
        self._session.add(m)
        await self._session.flush()
        return m.id
