from fastapi import HTTPException, status


class AppException(HTTPException):
    def __init__(self, status_code: int, error_code: str, message: str):
        super().__init__(status_code=status_code, detail={"code": error_code, "message": message})


class ValidationError(AppException):
    def __init__(self, message: str = "입력값이 올바르지 않습니다."):
        super().__init__(400, "VALIDATION_ERROR", message)


class AmountMismatchError(AppException):
    def __init__(self):
        super().__init__(400, "AMOUNT_MISMATCH", "결제 금액이 일치하지 않습니다.")


class UnauthorizedError(AppException):
    def __init__(self, message: str = "인증이 필요합니다."):
        super().__init__(401, "UNAUTHORIZED", message)


class ForbiddenError(AppException):
    def __init__(self, message: str = "권한이 없습니다."):
        super().__init__(403, "FORBIDDEN", message)


class UserNotFoundError(AppException):
    def __init__(self):
        super().__init__(404, "USER_NOT_FOUND", "사용자를 찾을 수 없습니다.")


class ProductNotFoundError(AppException):
    def __init__(self):
        super().__init__(404, "PRODUCT_NOT_FOUND", "상품을 찾을 수 없습니다.")


class OrderNotFoundError(AppException):
    def __init__(self):
        super().__init__(404, "ORDER_NOT_FOUND", "주문을 찾을 수 없습니다.")


class CouponNotFoundError(AppException):
    def __init__(self):
        super().__init__(404, "COUPON_NOT_FOUND", "쿠폰을 찾을 수 없습니다.")


class OutOfStockError(AppException):
    def __init__(self):
        super().__init__(409, "OUT_OF_STOCK", "재고가 부족합니다.")


class DuplicateEmailError(AppException):
    def __init__(self):
        super().__init__(409, "DUPLICATE_EMAIL", "이미 사용 중인 이메일입니다.")


class CouponExpiredError(AppException):
    def __init__(self):
        super().__init__(409, "COUPON_EXPIRED", "만료된 쿠폰입니다.")


class CouponOutOfStockError(AppException):
    def __init__(self):
        super().__init__(409, "COUPON_OUT_OF_STOCK", "쿠폰이 소진되었습니다.")


class AlreadyReviewedError(AppException):
    def __init__(self):
        super().__init__(409, "ALREADY_REVIEWED", "이미 리뷰를 작성한 상품입니다.")


class PaymentFailedError(AppException):
    def __init__(self, message: str = "결제 처리 중 오류가 발생했습니다."):
        super().__init__(500, "PAYMENT_FAILED", message)


class InvalidOrderStatusError(AppException):
    def __init__(self, message: str = "현재 상태에서 불가능한 작업입니다."):
        super().__init__(409, "INVALID_ORDER_STATUS", message)


class InsufficientPointError(AppException):
    def __init__(self):
        super().__init__(400, "INSUFFICIENT_POINT", "포인트가 부족합니다.")
