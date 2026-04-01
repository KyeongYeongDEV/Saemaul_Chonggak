from app.domain.common.exceptions import DomainException


class OrderNotFoundException(DomainException):
    def __init__(self):
        super().__init__("주문을 찾을 수 없습니다.")


class InvalidOrderStatusException(DomainException):
    def __init__(self, message: str = "현재 상태에서 불가능한 작업입니다."):
        super().__init__(message)
