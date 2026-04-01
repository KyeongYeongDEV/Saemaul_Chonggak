from app.domain.common.exceptions import DomainException


class PaymentFailedException(DomainException):
    def __init__(self, message: str = "결제 처리 중 오류가 발생했습니다."):
        super().__init__(message)


class AmountMismatchException(DomainException):
    def __init__(self, expected: int, received: int):
        super().__init__(
            f"결제 금액이 일치하지 않습니다. (예상: {expected}원, 수신: {received}원)"
        )
        self.expected = expected
        self.received = received
