from app.domain.common.exceptions import DomainException


class CouponNotFoundException(DomainException):
    def __init__(self):
        super().__init__("쿠폰을 찾을 수 없습니다.")


class CouponExpiredException(DomainException):
    def __init__(self):
        super().__init__("만료된 쿠폰입니다.")


class CouponOutOfStockException(DomainException):
    def __init__(self):
        super().__init__("쿠폰이 소진되었습니다.")


class AlreadyClaimedException(DomainException):
    def __init__(self):
        super().__init__("이미 발급받은 쿠폰입니다.")
