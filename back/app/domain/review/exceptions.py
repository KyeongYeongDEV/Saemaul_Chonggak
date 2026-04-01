from app.domain.common.exceptions import DomainException


class NotPurchasedException(DomainException):
    def __init__(self):
        super().__init__("구매한 상품에만 리뷰를 작성할 수 있습니다.")


class AlreadyReviewedException(DomainException):
    def __init__(self):
        super().__init__("이미 리뷰를 작성한 상품입니다.")
