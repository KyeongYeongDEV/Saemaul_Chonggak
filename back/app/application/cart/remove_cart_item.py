from dataclasses import dataclass

from app.domain.cart.repository import CartRepository


@dataclass
class RemoveCartItemCommand:
    user_id: int
    product_id: int | None  # None이면 전체 삭제


class RemoveCartItemUseCase:
    def __init__(self, cart_repo: CartRepository):
        self._cart_repo = cart_repo

    async def execute(self, cmd: RemoveCartItemCommand) -> None:
        if cmd.product_id is None:
            await self._cart_repo.delete(cmd.user_id)
        else:
            cart = await self._cart_repo.get(cmd.user_id)
            cart.remove_item(cmd.product_id)
            await self._cart_repo.save(cart)
