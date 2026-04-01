from dataclasses import dataclass
from datetime import datetime


@dataclass
class Faq:
    id: int | None
    category: str
    question: str
    answer: str
    sort_order: int
    is_active: bool
    created_at: datetime


@dataclass
class Notice:
    id: int | None
    title: str
    content: str
    is_pinned: bool
    is_active: bool
    created_at: datetime


@dataclass
class Inquiry:
    id: int | None
    user_id: int
    order_id: int | None
    title: str
    content: str
    status: str  # "pending" | "answered"
    answer: str | None
    answered_at: datetime | None
    created_at: datetime
