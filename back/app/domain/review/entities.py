from dataclasses import dataclass
from datetime import datetime

from app.domain.common.exceptions import DomainException


@dataclass
class Review:
    id: int | None
    user_id: int
    product_id: int
    order_id: int
    rating: int
    content: str | None
    created_at: datetime

    def __post_init__(self):
        if not (1 <= self.rating <= 5):
            raise DomainException("평점은 1~5 사이여야 합니다.")
