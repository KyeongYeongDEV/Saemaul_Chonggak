from dataclasses import dataclass

from app.core.config import settings
from app.core.security import decode_token
from app.infrastructure.cache.cache_service import CacheService


@dataclass
class LogoutCommand:
    access_token: str
    refresh_token: str | None


class LogoutUseCase:
    def __init__(self, cache: CacheService):
        self._cache = cache

    async def execute(self, cmd: LogoutCommand) -> None:
        try:
            payload = decode_token(cmd.access_token)
            jti = payload.get("jti")
            user_id = int(payload["sub"])
            if jti:
                ttl = settings.JWT_ACCESS_EXPIRE_MINUTES * 60
                await self._cache.blacklist_access_token(jti, ttl)
        except Exception:
            pass

        if cmd.refresh_token:
            try:
                payload = decode_token(cmd.refresh_token)
                user_id = int(payload["sub"])
                jti = payload.get("jti")
                if jti:
                    await self._cache.delete_refresh_token(user_id, jti)
            except Exception:
                pass
