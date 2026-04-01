from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

from app.domain.user.exceptions import InsufficientPointException


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


@dataclass
class UserAddress:
    id: int | None
    user_id: int
    name: str
    receiver: str
    phone: str
    zipcode: str
    address1: str
    address2: str | None
    is_default: bool


@dataclass
class User:
    id: int | None
    email: str
    password: str  # bcrypt hash
    name: str
    phone: str | None
    role: UserRole
    is_active: bool
    point: int
    created_at: datetime
    updated_at: datetime | None = None

    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN

    def deduct_point(self, amount: int) -> None:
        if self.point < amount:
            raise InsufficientPointException()
        self.point -= amount

    def earn_point(self, amount: int) -> None:
        self.point += amount
