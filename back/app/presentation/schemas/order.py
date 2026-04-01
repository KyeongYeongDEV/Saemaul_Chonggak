from pydantic import BaseModel


class OrderItemResponse(BaseModel):
    product_id: int
    product_name: str
    price: int
    quantity: int
    subtotal: int


class OrderResponse(BaseModel):
    id: int
    order_no: str
    status: str
    items: list[OrderItemResponse]
    total_amount: int
    discount_amount: int
    shipping_fee: int
    final_amount: int
    receiver_name: str
    receiver_phone: str
    zipcode: str
    address1: str
    address2: str | None
    memo: str | None
    created_at: str


class CancelOrderRequest(BaseModel):
    reason: str = "고객 요청"


class ExchangeReturnRequest(BaseModel):
    reason: str
