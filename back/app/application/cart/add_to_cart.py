from dataclasses import dataclass

from app.core.exceptions import OutOfStockError, ProductNotFoundError
from app.domain.cart.repository import CartRepository
from app.domain.product.repository import ProductRepository


@dataclass
class AddToCartCommand:
    user_id: int
    product_id: int
    quantity: int


class AddToCartUseCase:
    def __init__(self, cart_repo: CartRepository, product_repo: ProductRepository):
        self._cart_repo = cart_repo
        self._product_repo = product_repo

    async def execute(self, cmd: AddToCartCommand) -> None:
        product = await self._product_repo.get_by_id(cmd.product_id)
        if not product or not product.is_active:
            raise ProductNotFoundError()
        if product.stock < cmd.quantity:
            raise OutOfStockError()

        cart = await self._cart_repo.get(cmd.user_id)
        cart.add_item(cmd.product_id, cmd.quantity)
        await self._cart_repo.save(cart)
