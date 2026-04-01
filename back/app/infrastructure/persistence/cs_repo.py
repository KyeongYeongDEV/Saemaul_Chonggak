from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.cs.entities import Faq, Inquiry, Notice
from app.domain.cs.repository import FaqRepository, InquiryRepository, NoticeRepository
from app.infrastructure.persistence.models import FaqModel, InquiryModel, NoticeModel


def _to_faq(m: FaqModel) -> Faq:
    return Faq(
        id=m.id,
        category=m.category,
        question=m.question,
        answer=m.answer,
        sort_order=m.sort_order,
        is_active=m.is_active,
        created_at=m.created_at,
    )


def _to_notice(m: NoticeModel) -> Notice:
    return Notice(
        id=m.id,
        title=m.title,
        content=m.content,
        is_pinned=m.is_pinned,
        is_active=m.is_active,
        created_at=m.created_at,
    )


def _to_inquiry(m: InquiryModel) -> Inquiry:
    return Inquiry(
        id=m.id,
        user_id=m.user_id,
        order_id=m.order_id,
        title=m.title,
        content=m.content,
        status=m.status,
        answer=m.answer,
        answered_at=m.answered_at,
        created_at=m.created_at,
    )


class SQLFaqRepository(FaqRepository):
    def __init__(self, session: AsyncSession):
        self._s = session

    async def list_active(self) -> list[Faq]:
        result = await self._s.execute(
            select(FaqModel)
            .where(FaqModel.is_active == True)
            .order_by(FaqModel.sort_order)
        )
        return [_to_faq(m) for m in result.scalars()]


class SQLNoticeRepository(NoticeRepository):
    def __init__(self, session: AsyncSession):
        self._s = session

    async def list_active(self, page: int, size: int) -> tuple[list[Notice], int]:
        q = (
            select(NoticeModel)
            .where(NoticeModel.is_active == True)
            .order_by(NoticeModel.is_pinned.desc(), NoticeModel.created_at.desc())
            .offset((page - 1) * size)
            .limit(size)
        )
        count_q = (
            select(func.count())
            .select_from(NoticeModel)
            .where(NoticeModel.is_active == True)
        )
        result = await self._s.execute(q)
        total = await self._s.scalar(count_q)
        return [_to_notice(m) for m in result.scalars()], total or 0


class SQLInquiryRepository(InquiryRepository):
    def __init__(self, session: AsyncSession):
        self._s = session

    async def list_by_user(
        self, user_id: int, page: int, size: int
    ) -> tuple[list[Inquiry], int]:
        q = (
            select(InquiryModel)
            .where(InquiryModel.user_id == user_id)
            .order_by(InquiryModel.created_at.desc())
            .offset((page - 1) * size)
            .limit(size)
        )
        count_q = (
            select(func.count())
            .select_from(InquiryModel)
            .where(InquiryModel.user_id == user_id)
        )
        result = await self._s.execute(q)
        total = await self._s.scalar(count_q)
        return [_to_inquiry(m) for m in result.scalars()], total or 0

    async def save(self, inquiry: Inquiry) -> Inquiry:
        m = InquiryModel(
            user_id=inquiry.user_id,
            order_id=inquiry.order_id,
            title=inquiry.title,
            content=inquiry.content,
        )
        self._s.add(m)
        await self._s.flush()
        await self._s.refresh(m)
        return _to_inquiry(m)
