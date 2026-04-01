from app.domain.common.exceptions import DomainException


class ProductNotFoundException(DomainException):
    def __init__(self):
        super().__init__("상품을 찾을 수 없습니다.")


class OutOfStockException(DomainException):
    def __init__(self):
        super().__init__("재고가 부족합니다.")
