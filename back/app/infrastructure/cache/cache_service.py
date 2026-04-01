import json
from collections.abc import Callable, Coroutine
from typing import Any

from redis.asyncio import Redis

# Lua script: 원자적 재고 감소
_DECR_IF_POSITIVE = """
local key = KEYS[1]
local stock = redis.call('GET', key)
if not stock or tonumber(stock) <= 0 then
    return -1
end
return redis.call('DECR', key)
"""


class CacheService:
    def __init__(self, redis: Redis):
        self._r = redis

    async def get_or_set(self, key: str, ttl: int, loader: Callable[[], Coroutine]) -> Any:
        """Cache-Aside 패턴."""
        cached = await self._r.get(key)
        if cached:
            return json.loads(cached)
        data = await loader()
        if data is not None:
            await self._r.setex(key, ttl, json.dumps(data, default=str))
        return data

    async def invalidate(self, key: str) -> None:
        await self._r.delete(key)

    async def invalidate_pattern(self, pattern: str) -> None:
        # KEYS 대신 SCAN 사용 — KEYS는 Redis 단일 스레드 블로킹으로 운영 장애 유발
        cursor = 0
        while True:
            cursor, keys = await self._r.scan(cursor, match=pattern, count=100)
            if keys:
                await self._r.delete(*keys)
            if cursor == 0:
                break

    async def atomic_decr_stock(self, key: str) -> int:
        """재고 원자적 감소. 재고 없으면 -1 반환."""
        result = await self._r.eval(_DECR_IF_POSITIVE, 1, key)
        return int(result)

    async def init_stock(self, key: str, stock: int, ttl: int) -> None:
        await self._r.setex(key, ttl, stock)

    async def track_mau(self, year_month: str, user_id: int) -> None:
        key = f"mau:{year_month}"
        await self._r.sadd(key, user_id)
        await self._r.expire(key, 2592000)  # 30일

    async def get_mau(self, year_month: str) -> int:
        return await self._r.scard(f"mau:{year_month}")

    async def blacklist_access_token(self, jti: str, ttl: int) -> None:
        await self._r.setex(f"blacklist:access:{jti}", ttl, "1")

    async def store_refresh_token(self, user_id: int, jti: str, ttl: int) -> None:
        await self._r.setex(f"session:refresh:{user_id}:{jti}", ttl, "1")

    async def delete_refresh_token(self, user_id: int, jti: str) -> None:
        await self._r.delete(f"session:refresh:{user_id}:{jti}")

    async def refresh_token_exists(self, user_id: int, jti: str) -> bool:
        return bool(await self._r.exists(f"session:refresh:{user_id}:{jti}"))
