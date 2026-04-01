from pydantic import BaseModel


class AddToCartRequest(BaseModel):
    product_id: int
    quantity: int = 1


class UpdateCartItemRequest(BaseModel):
    quantity: int


class CartItemResponse(BaseModel):
    product_id: int
    product_name: str
    thumbnail_url: str | None
    unit_price: int
    quantity: int
    subtotal: int


class CartResponse(BaseModel):
    items: list[CartItemResponse]
    total_amount: int
    item_count: int
