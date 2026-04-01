from abc import ABC, abstractmethod

from app.domain.cart.entities import Cart


class CartRepository(ABC):
    @abstractmethod
    async def get(self, user_id: int) -> Cart: ...

    @abstractmethod
    async def save(self, cart: Cart) -> None: ...

    @abstractmethod
    async def delete(self, user_id: int) -> None: ...
