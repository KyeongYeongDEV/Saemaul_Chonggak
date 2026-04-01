from app.domain.common.exceptions import DomainException


class UserNotFoundException(DomainException):
    def __init__(self):
        super().__init__("사용자를 찾을 수 없습니다.")


class DuplicateEmailException(DomainException):
    def __init__(self):
        super().__init__("이미 사용 중인 이메일입니다.")


class InvalidPasswordException(DomainException):
    def __init__(self):
        super().__init__("비밀번호가 올바르지 않습니다.")


class InsufficientPointException(DomainException):
    def __init__(self):
        super().__init__("포인트가 부족합니다.")
