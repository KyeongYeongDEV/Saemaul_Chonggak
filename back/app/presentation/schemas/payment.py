from pydantic import BaseModel


class PreparePaymentRequest(BaseModel):
    address_id: int
    coupon_id: int | None = None
    point_use: int = 0
    memo: str | None = None


class PreparePaymentResponse(BaseModel):
    order_no: str
    amount: int
    order_name: str


class ConfirmPaymentRequest(BaseModel):
    payment_key: str
    order_no: str
    amount: int


class ConfirmPaymentResponse(BaseModel):
    order_no: str
    amount: int
    method: str | None


class CancelPaymentRequest(BaseModel):
    cancel_reason: str
