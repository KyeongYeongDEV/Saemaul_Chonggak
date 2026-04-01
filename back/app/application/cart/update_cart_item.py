from dataclasses import dataclass

from app.domain.cart.repository import CartRepository


@dataclass
class UpdateCartItemCommand:
    user_id: int
    product_id: int
    quantity: int


class UpdateCartItemUseCase:
    def __init__(self, cart_repo: CartRepository):
        self._cart_repo = cart_repo

    async def execute(self, cmd: UpdateCartItemCommand) -> None:
        cart = await self._cart_repo.get(cmd.user_id)
        if cmd.quantity <= 0:
            cart.remove_item(cmd.product_id)
        else:
            cart.update_item(cmd.product_id, cmd.quantity)
        await self._cart_repo.save(cart)
