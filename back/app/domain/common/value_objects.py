from dataclasses import dataclass

from app.domain.common.exceptions import DomainException


@dataclass(frozen=True)
class Money:
    amount: int

    def __post_init__(self):
        if self.amount < 0:
            raise DomainException("금액은 0 이상이어야 합니다.")

    def __add__(self, other: "Money") -> "Money":
        return Money(self.amount + other.amount)

    def __sub__(self, other: "Money") -> "Money":
        result = self.amount - other.amount
        if result < 0:
            raise DomainException("금액이 부족합니다.")
        return Money(result)


@dataclass(frozen=True)
class PhoneNumber:
    value: str

    def __post_init__(self):
        digits = self.value.replace("-", "")
        if not digits.isdigit() or len(digits) < 10:
            raise DomainException("올바른 전화번호 형식이 아닙니다.")


@dataclass(frozen=True)
class Address:
    zipcode: str
    address1: str
    address2: str | None
