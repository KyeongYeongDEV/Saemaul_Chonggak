class DomainException(Exception):
    """도메인 레이어 예외 베이스. 외부 의존성 없음."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)
