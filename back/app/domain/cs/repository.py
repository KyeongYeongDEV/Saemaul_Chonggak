from abc import ABC, abstractmethod

from app.domain.cs.entities import Faq, Inquiry, Notice


class FaqRepository(ABC):
    @abstractmethod
    async def list_active(self) -> list[Faq]: ...


class NoticeRepository(ABC):
    @abstractmethod
    async def list_active(
        self, page: int, size: int
    ) -> tuple[list[Notice], int]: ...


class InquiryRepository(ABC):
    @abstractmethod
    async def list_by_user(
        self, user_id: int, page: int, size: int
    ) -> tuple[list[Inquiry], int]: ...

    @abstractmethod
    async def save(self, inquiry: Inquiry) -> Inquiry: ...
