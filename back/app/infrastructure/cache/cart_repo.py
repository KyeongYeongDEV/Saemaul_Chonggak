from redis.asyncio import Redis

from app.domain.cart.entities import Cart, CartItem
from app.domain.cart.repository import CartRepository

CART_TTL = 604800  # 7일


class RedisCartRepository(CartRepository):
    def __init__(self, redis: Redis):
        self._r = redis

    def _key(self, user_id: int) -> str:
        return f"cart:{user_id}"

    async def get(self, user_id: int) -> Cart:
        raw = await self._r.hgetall(self._key(user_id))
        items = [CartItem(product_id=int(pid), quantity=int(qty)) for pid, qty in raw.items()]
        return Cart(user_id=user_id, items=items)

    async def save(self, cart: Cart) -> None:
        key = self._key(cart.user_id)
        await self._r.delete(key)
        if cart.items:
            mapping = {str(item.product_id): item.quantity for item in cart.items}
            await self._r.hset(key, mapping=mapping)
            await self._r.expire(key, CART_TTL)

    async def delete(self, user_id: int) -> None:
        await self._r.delete(self._key(user_id))
