from dataclasses import dataclass

from app.domain.cart.entities import Cart
from app.domain.cart.repository import CartRepository
from app.domain.product.repository import ProductRepository


@dataclass
class CartItemDetail:
    product_id: int
    product_name: str
    thumbnail_url: str | None
    unit_price: int
    quantity: int
    subtotal: int


@dataclass
class CartDetail:
    items: list[CartItemDetail]
    total_amount: int
    item_count: int


class GetCartUseCase:
    def __init__(self, cart_repo: CartRepository, product_repo: ProductRepository):
        self._cart_repo = cart_repo
        self._product_repo = product_repo

    async def execute(self, user_id: int) -> CartDetail:
        cart = await self._cart_repo.get(user_id)
        details = []
        total = 0
        for item in cart.items:
            product = await self._product_repo.get_by_id(item.product_id)
            if product and product.is_active:
                price = product.effective_price()
                subtotal = price * item.quantity
                total += subtotal
                details.append(CartItemDetail(
                    product_id=item.product_id,
                    product_name=product.name,
                    thumbnail_url=product.thumbnail_url,
                    unit_price=price,
                    quantity=item.quantity,
                    subtotal=subtotal,
                ))
        return CartDetail(items=details, total_amount=total, item_count=sum(d.quantity for d in details))
